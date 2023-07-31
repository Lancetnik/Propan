from functools import partial
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

import aiokafka
from fast_depends.dependencies import Depends
from kafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from typing_extensions import Literal

from propan.__about__ import __version__
from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.push_back_watcher import BaseWatcher
from propan.broker.schemas import HandlerCallWrapper, Publisher
from propan.broker.types import (
    AsyncDecoder,
    AsyncParser,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.kafka.handler import Handler
from propan.kafka.message import KafkaMessage
from propan.kafka.shared.logging import KafkaLoggingMixin
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context
from propan.utils.functions import to_async


class KafkaBroker(
    KafkaLoggingMixin,
    BrokerAsyncUsecase[aiokafka.ConsumerRecord, AnyDict],
):
    handlers: Dict[str, Handler]
    _publisher: Optional[aiokafka.AIOKafkaProducer]

    def __init__(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
        response_topic: str = "",
        protocol: str = "kafka",
        api_version: str = "auto",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            url=bootstrap_servers,
            protocol=protocol,
            protocol_version=api_version,
            **kwargs,
            bootstrap_servers=bootstrap_servers,
        )
        self.response_topic = response_topic
        self._publisher = None

    async def _close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        if self._publisher is not None:
            await self._publisher.stop()
            self._publisher = None

        await super()._close(exc_type, exc_val, exec_tb)

    async def connect(
        self,
        *args: Any,
        **kwargs: AnyDict,
    ) -> AnyDict:
        connection = await super().connect(*args, **kwargs)
        for p in self._publishers:
            p._publisher = self._publisher
        return connection

    async def _connect(
        self,
        **kwargs: AnyDict,
    ) -> AnyDict:
        kwargs["client_id"] = kwargs.get("client_id", "propan-" + __version__)

        producer = aiokafka.AIOKafkaProducer(**kwargs)
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
        return consumer_kwargs

    async def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, ""),
        )

        await super().start()

        for handler in self.handlers.values():
            c = self._get_log_context(None, handler.topics)
            self._log(f"`{handler.name}` waiting for messages", extra=c)
            await handler.start(**self._connection)

    async def _process_message(
        self,
        func: Callable[[KafkaMessage], Awaitable[T_HandlerReturn]],
        call_wrapper: HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        watcher: BaseWatcher | None,
    ) -> Callable[[KafkaMessage], Awaitable[T_HandlerReturn]]:
        return super()._process_message(func, call_wrapper, watcher)

    def subscriber(
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
        # broker arguments
        dependencies: Sequence[Depends] = (),
        parser: Optional[AsyncParser[aiokafka.ConsumerRecord]] = None,
        decoder: Optional[AsyncDecoder[aiokafka.ConsumerRecord]] = None,
        middlewares: Optional[
            List[
                Callable[
                    [KafkaMessage],
                    AsyncContextManager[None],
                ]
            ]
        ] = None,
        filter: Callable[
            [KafkaMessage],
            Union[bool, Awaitable[bool]],
        ] = lambda m: not m.processed,
        # AsyncAPI information
        description: Optional[str] = None,
        **original_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        Any,  # AMQPHandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        super().subscriber()

        self._setup_log_context(topics)

        key = "".join(topics)
        builder = partial(
            aiokafka.AIOKafkaConsumer,
            group_id=group_id,
            key_deserializer=key_deserializer,
            value_deserializer=value_deserializer,
            fetch_max_wait_ms=fetch_max_wait_ms,
            fetch_max_bytes=fetch_max_bytes,
            fetch_min_bytes=fetch_min_bytes,
            max_partition_fetch_bytes=max_partition_fetch_bytes,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            auto_commit_interval_ms=auto_commit_interval_ms,
            check_crcs=check_crcs,
            partition_assignment_strategy=partition_assignment_strategy,
            max_poll_interval_ms=max_poll_interval_ms,
            rebalance_timeout_ms=rebalance_timeout_ms,
            session_timeout_ms=session_timeout_ms,
            heartbeat_interval_ms=heartbeat_interval_ms,
            consumer_timeout_ms=consumer_timeout_ms,
            max_poll_records=max_poll_records,
            exclude_internal_topics=exclude_internal_topics,
            isolation_level=isolation_level,
        )
        handler = self.handlers.get(
            key,
            Handler(
                *topics,
                builder=builder,
                description=description,
            ),
        )

        self.handlers[key] = handler

        def consumer_wrapper(
            func: Callable[P_HandlerParams, T_HandlerReturn],
        ) -> Any:  # AMQPHandlerCallWrapper[P_HandlerParams, T_HandlerReturn]:
            # handler_call: AMQPHandlerCallWrapper
            wrapped_func, handler_call, dependant = self._wrap_handler(
                func=func,
                extra_dependencies=dependencies,
                **original_kwargs,
                topics=topics,
            )

            handler.add_call(
                handler=handler_call,
                wrapped_call=wrapped_func,
                filter=to_async(filter),
                middlewares=middlewares,
                parser=parser or self._global_parser,
                decoder=decoder or self._global_decoder,
                dependant=dependant,
            )

            return handler_call

        return consumer_wrapper

    def publisher(self, publisher: Publisher) -> Publisher:
        return super().publisher(publisher)

    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        reply_to: str = "",
        rpc: bool = False,
        rpc_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        return await super().publish(
            message,
            *args,
            reply_to=reply_to,
            rpc=rpc,
            rpc_timeout=rpc_timeout,
            raise_timeout=raise_timeout,
            **kwargs,
        )
