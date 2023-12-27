import asyncio
import logging
from functools import partial, wraps
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from uuid import uuid4

import anyio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from aiokafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from aiokafka.structs import ConsumerRecord
from fast_depends.dependencies import Depends
from typing_extensions import Literal, TypeAlias, TypeVar

from propan.__about__ import __version__
from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import SkipMessage
from propan.brokers.kafka.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils.context import context

T = TypeVar("T")
CorrelationId: TypeAlias = str
KafkaMessage: TypeAlias = PropanMessage[ConsumerRecord]


class KafkaBroker(
    BrokerAsyncUsecase[ConsumerRecord, Callable[[Tuple[str, ...]], AIOKafkaConsumer]]
):
    _publisher: Optional[AIOKafkaProducer]
    __max_topic_len: int
    response_topic: str
    response_callbacks: Dict[CorrelationId, "asyncio.Future[DecodedMessage]"]
    handlers: List[Handler]

    def __init__(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
        response_topic: str = "",
        log_fmt: Optional[str] = None,
        protocol: str = "kafka",
        api_version: str = "auto",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            bootstrap_servers,
            log_fmt=log_fmt,
            url_=bootstrap_servers,
            protocol=protocol,
            protocol_version=api_version,
            **kwargs,
        )
        self.__max_topic_len = 4
        self._publisher = None
        self.response_topic = response_topic
        self.response_callbacks = {}

    async def _connect(
        self,
        **kwargs: Any,
    ) -> AIOKafkaConsumer:
        kwargs["client_id"] = kwargs.get("client_id", "propan-" + __version__)

        producer = AIOKafkaProducer(**kwargs)
        context.set_global("producer", producer)
        await producer.start()
        self._publisher = producer
        consumer_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            in {
                "bootstrap_servers",
                "loop",
                "client_id",
                "request_timeout_ms",
                "retry_backoff_ms",
                "metadata_max_age_ms",
                "security_protocol",
                "api_version",
                "connections_max_idle_ms",
                "sasl_mechanism",
                "sasl_plain_password",
                "sasl_plain_username",
                "sasl_kerberos_service_name",
                "sasl_kerberos_domain_name",
                "sasl_oauth_token_provider",
                "ssl_context",
            }
            and v
        }
        return partial(AIOKafkaConsumer, **consumer_kwargs)

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)

        for f in self.response_callbacks.values():
            f.cancel()
        self.response_callbacks = {}

        for handler in self.handlers:
            if handler.task is not None:
                handler.task.cancel()
                handler.task = None

            if handler.consumer is not None:
                await handler.consumer.stop()
                handler.consumer = None

        if self._publisher is not None:
            await self._publisher.stop()
            self._publisher = None

    def handle(
        self,
        *topics: str,
        group_id: Optional[str] = None,
        key_deserializer: Optional[Callable[[bytes], Any]] = None,
        value_deserializer: Optional[Callable[[bytes], Any]] = None,
        fetch_max_wait_ms: int = 500,
        fetch_max_bytes: int = 52428800,
        fetch_min_bytes: int = 1,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal[
            "latest",
            "earliest",
            "none",
        ] = "latest",
        enable_auto_commit: bool = True,
        auto_commit_interval_ms: int = 5000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence[AbstractPartitionAssignor] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 300000,
        rebalance_timeout_ms: Optional[int] = None,
        session_timeout_ms: int = 10000,
        heartbeat_interval_ms: int = 3000,
        consumer_timeout_ms: int = 200,
        max_poll_records: Optional[int] = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted",
            "read_committed",
        ] = "read_uncommitted",
        ## broker
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle()

        def wrapper(
            func: HandlerCallable[T_HandlerReturn],
        ) -> Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]]:
            for t in topics:
                self.__max_topic_len = max((self.__max_topic_len, len(t)))

            func, dependant = self._wrap_handler(
                func,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                topics=topics,
                _description=description,
                group_id=group_id,
                consumer_kwargs={
                    "key_deserializer": key_deserializer,
                    "value_deserializer": value_deserializer,
                    "fetch_max_wait_ms": fetch_max_wait_ms,
                    "fetch_max_bytes": fetch_max_bytes,
                    "fetch_min_bytes": fetch_min_bytes,
                    "max_partition_fetch_bytes": max_partition_fetch_bytes,
                    "auto_offset_reset": auto_offset_reset,
                    "enable_auto_commit": enable_auto_commit,
                    "auto_commit_interval_ms": auto_commit_interval_ms,
                    "check_crcs": check_crcs,
                    "partition_assignment_strategy": partition_assignment_strategy,
                    "max_poll_interval_ms": max_poll_interval_ms,
                    "rebalance_timeout_ms": rebalance_timeout_ms,
                    "session_timeout_ms": session_timeout_ms,
                    "heartbeat_interval_ms": heartbeat_interval_ms,
                    "consumer_timeout_ms": consumer_timeout_ms,
                    "max_poll_records": max_poll_records,
                    "exclude_internal_topics": exclude_internal_topics,
                    "isolation_level": isolation_level,
                },
                dependant=dependant,
            )
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        if self.response_topic:
            self.handle(
                self.response_topic,
                _raw=True,
                enable_auto_commit=False,
            )(self._consume_response)

        context.set_local(
            "log_context",
            self._get_log_context(None, ""),
        )

        await super().start()

        for handler in self.handlers:  # pragma: no branch
            c = self._get_log_context(None, handler.topics)
            self._log(f"`{handler.callback.__name__}` waiting for messages", extra=c)

            consumer = self._connection(
                *handler.topics,
                group_id=handler.group_id,
                **handler.consumer_kwargs,
            )
            await consumer.start()
            handler.consumer = consumer
            handler.task = asyncio.create_task(self._consume(handler))

    @staticmethod
    async def _parse_message(message: ConsumerRecord) -> KafkaMessage:
        headers = {i: j.decode() for i, j in message.headers}
        return PropanMessage(
            body=message.value,
            raw_message=message,
            message_id=f"{message.offset}-{message.timestamp}",
            reply_to=headers.get("reply_to", ""),
            content_type=headers.get("content-type"),
            headers=headers,
        )

    def _process_message(
        self,
        func: Callable[[KafkaMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[KafkaMessage], Awaitable[T]]:
        @wraps(func)
        async def wrapper(message: KafkaMessage) -> T:
            r = await func(message)

            if message.reply_to:
                await self.publish(
                    message=r or "",
                    headers={"correlation_id": message.headers.get("correlation_id")},
                    topic=message.reply_to,
                )

            return r

        return wrapper

    async def publish(
        self,
        message: SendableMessage,
        topic: str,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
    ) -> Optional[DecodedMessage]:
        message, content_type = super()._encode_message(message)

        headers_to_send = {
            "content-type": content_type or "",
            **(headers or {}),
        }

        if callback is True:
            reply_to = reply_to or self.response_topic
            if not reply_to:
                raise ValueError(
                    "You should specify `response_topic` at init or use `reply_to` argument"
                )

        if reply_to:
            correlation_id = str(uuid4())
            headers_to_send.update(
                {
                    "reply_to": reply_to,
                    "correlation_id": correlation_id,
                }
            )
        else:
            correlation_id = ""

        response_future: Optional["asyncio.Future[DecodedMessage]"]
        if callback is True:
            response_future = asyncio.Future()
            self.response_callbacks[correlation_id] = response_future
        else:
            response_future = None

        await self._publisher.send(
            topic=topic,
            value=message,
            key=key,
            partition=partition,
            timestamp_ms=timestamp_ms,
            headers=[(i, j.encode()) for i, j in headers_to_send.items()],
        )

        if response_future is not None:
            if raise_timeout:
                scope = anyio.fail_after
            else:
                scope = anyio.move_on_after

            msg: Any = None
            with scope(callback_timeout):
                msg = await response_future

            if msg:
                return await self._decode_message(msg)

    async def publish_batch(
        self,
        *msgs: SendableMessage,
        topic: str,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        batch = self._publisher.create_batch()

        for msg in msgs:
            message, content_type = super()._encode_message(msg)

            headers_to_send = {
                "content-type": content_type or "",
                **(headers or {}),
            }

            batch.append(
                key=None,
                value=message,
                timestamp=timestamp_ms,
                headers=[(i, j.encode()) for i, j in headers_to_send.items()],
            )

        await self._publisher.send_batch(batch, topic, partition=partition)

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(topic)-{self.__max_topic_len}s | "
            "%(message_id)-10s "
            "- %(message)s"
        )

    def _get_log_context(
        self,
        message: Optional[KafkaMessage],
        topics: Sequence[str] = (),
    ) -> Dict[str, Any]:
        if topics:
            topic = ", ".join(topics)
        elif message is not None:
            topic = message.raw_message.topic
        else:
            topic = ""

        return {
            "topic": topic,
            **super()._get_log_context(message),
        }

    async def _consume(self, handler: Handler) -> NoReturn:
        c = self._get_log_context(None, handler.topics)

        connected = True
        while True:
            try:
                msg = await handler.consumer.getone()

            except Exception as e:
                if connected is True:
                    self._log(e, logging.WARNING, c, exc_info=e)
                    connected = False
                await anyio.sleep(5)

            else:
                if connected is False:
                    self._log("Connection established", logging.INFO, c)
                    connected = True

                await handler.callback(msg)

    async def _consume_response(self, message: KafkaMessage):
        correlation_id = message.headers.get("correlation_id")
        if correlation_id is not None:
            callback = self.response_callbacks.pop(correlation_id, None)
            if callback is not None:
                callback.set_result(message)

        raise SkipMessage()
