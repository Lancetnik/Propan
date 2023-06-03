import asyncio
import logging
from functools import partial, wraps
from typing import Any, Callable, Dict, List, NoReturn, Optional, Sequence, Tuple, Union
from uuid import uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import ConsumerRecord
from typing_extensions import TypeAlias, TypeVar

from propan.__about__ import __version__
from propan.brokers._model.broker_usecase import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import SkipMessage
from propan.brokers.kafka.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import (
    AnyCallable,
    AnyDict,
    DecodedMessage,
    DecoratedCallable,
    SendableMessage,
    Wrapper,
)
from propan.utils.context import context

T = TypeVar("T")
CorrelationId: TypeAlias = str


class KafkaBroker(BrokerUsecase):
    _publisher: Optional[AIOKafkaProducer]
    _connection: Callable[[Tuple[str, ...]], AIOKafkaConsumer]
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
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(bootstrap_servers, log_fmt=log_fmt, **kwargs)
        self.__max_topic_len = 4
        self._publisher = None
        self.response_topic = response_topic
        self.response_callbacks = {}

    async def _connect(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        **kwargs: Any,
    ) -> AIOKafkaConsumer:
        kwargs["client_id"] = kwargs.get("client_id", "propan-" + __version__)
        kwargs["bootstrap_servers"] = bootstrap_servers

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
            }
            and v
        }
        return partial(AIOKafkaConsumer, **consumer_kwargs)

    async def close(self) -> None:
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
        _raw: bool = False,
        **kwargs: AnyDict,
    ) -> Wrapper:
        def wrapper(func: AnyCallable) -> DecoratedCallable:
            for t in topics:
                self.__max_topic_len = max((self.__max_topic_len, len(t)))

            func = self._wrap_handler(func, _raw=_raw)
            handler = Handler(
                callback=func,
                topics=topics,
                consumer_kwargs=kwargs,
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

            consumer = self._connection(*handler.topics, **handler.consumer_kwargs)
            await consumer.start()
            handler.consumer = consumer
            handler.task = asyncio.create_task(self._consume(handler))

    @staticmethod
    async def _parse_message(message: ConsumerRecord) -> PropanMessage:
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
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
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
            try:
                response = await asyncio.wait_for(response_future, callback_timeout)
            except asyncio.TimeoutError as e:
                if raise_timeout is True:
                    raise e
                return None
            else:
                return response

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
        message: Optional[PropanMessage],
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

        while True:
            try:
                msg = await handler.consumer.getone()
            except Exception as e:
                self._log(e, logging.WATNING, c)
            else:
                await handler.callback(msg)

    async def _consume_response(self, message: PropanMessage):
        correlation_id = message.headers.get("correlation_id")
        if correlation_id is not None:
            callback = self.response_callbacks.pop(correlation_id, None)
            if callback is not None:
                callback.set_result(await self._decode_message(message))

        raise SkipMessage()
