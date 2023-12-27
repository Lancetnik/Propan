import logging
from asyncio import AbstractEventLoop, Future
from ssl import SSLContext
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.abc import AbstractTokenProvider
from aiokafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from aiokafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from aiokafka.producer.producer import _missing
from aiokafka.structs import ConsumerRecord
from fast_depends.dependencies import Depends
from kafka.partitioner.default import DefaultPartitioner
from typing_extensions import Literal, TypeAlias, TypeVar

from propan.__about__ import __version__
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.kafka.schemas import Handler
from propan.brokers.middlewares import BaseMiddleware
from propan.brokers.push_back_watcher import BaseWatcher
from propan.log import access_logger
from propan.types import DecodedMessage, SendableMessage

Partition = TypeVar("Partition")
CorrelationId: TypeAlias = str
KafkaMessage: TypeAlias = PropanMessage[ConsumerRecord]

class KafkaBroker(
    BrokerAsyncUsecase[ConsumerRecord, Callable[[Tuple[str, ...]], AIOKafkaConsumer]]
):
    _publisher: Optional[AIOKafkaProducer]
    __max_topic_len: int
    response_topic: str
    response_callbacks: Dict[CorrelationId, "Future[DecodedMessage]"]
    handlers: List[Handler]
    middlewares: Sequence[Type[BaseMiddleware[ConsumerRecord]]]

    def __init__(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
        response_topic: str = "",
        # both
        client_id: str = "propan-" + __version__,
        request_timeout_ms: int = 40 * 1000,
        retry_backoff_ms: int = 100,
        metadata_max_age_ms: int = 5 * 60 * 1000,
        security_protocol: Literal[
            "SSL",
            "PLAINTEXT",
        ] = "PLAINTEXT",
        api_version: str = "auto",
        connections_max_idle_ms: int = 540000,
        sasl_mechanism: Literal[
            "PLAIN",
            "GSSAPI",
            "SCRAM-SHA-256",
            "SCRAM-SHA-512",
            "OAUTHBEARER",
        ] = "PLAIN",
        sasl_plain_password: Optional[str] = None,
        sasl_plain_username: Optional[str] = None,
        sasl_kerberos_service_name: str = "kafka",
        sasl_kerberos_domain_name: Optional[str] = None,
        sasl_oauth_token_provider: Optional[AbstractTokenProvider] = None,
        # publisher
        acks: Union[Literal[0, 1, -1, "all"], object] = _missing,
        key_serializer: Optional[Callable[[Any], bytes]] = None,
        value_serializer: Optional[Callable[[Any], bytes]] = None,
        compression_type: Optional[Literal["gzip", "snappy", "lz4", "zstd"]] = None,
        max_batch_size: int = 16384,
        partitioner: Callable[
            [bytes, List[Partition], List[Partition]],
            Partition,
        ] = DefaultPartitioner(),
        max_request_size: int = 1048576,
        linger_ms: int = 0,
        send_backoff_ms: int = 100,
        ssl_context: Optional[SSLContext] = None,
        enable_idempotence: bool = False,
        transactional_id: Optional[str] = None,
        transaction_timeout_ms: int = 60000,
        loop: Optional[AbstractEventLoop] = None,
        # broker
        logger: Optional[logging.Logger] = access_logger,
        decode_message: AsyncDecoder[ConsumerRecord] = None,
        parse_message: AsyncParser[ConsumerRecord] = None,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        dependencies: Sequence[Depends] = (),
        middlewares: Sequence[Type[BaseMiddleware[ConsumerRecord]]] = (),
        protocol: str = "kafka",
    ) -> None: ...
    async def connect(
        self,
        *,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        # both
        loop: Optional[AbstractEventLoop] = None,
        client_id: str = "propan-" + __version__,
        request_timeout_ms: int = 40 * 1000,
        retry_backoff_ms: int = 100,
        metadata_max_age_ms: int = 5 * 60 * 1000,
        security_protocol: Literal[
            "SSL",
            "PLAINTEXT",
        ] = "PLAINTEXT",
        api_version: str = "auto",
        connections_max_idle_ms: int = 540000,
        sasl_mechanism: Literal[
            "PLAIN",
            "GSSAPI",
            "SCRAM-SHA-256",
            "SCRAM-SHA-512",
            "OAUTHBEARER",
        ] = "PLAIN",
        sasl_plain_password: Optional[str] = None,
        sasl_plain_username: Optional[str] = None,
        sasl_kerberos_service_name: str = "kafka",
        sasl_kerberos_domain_name: Optional[str] = None,
        sasl_oauth_token_provider: Optional[AbstractTokenProvider] = None,
        # publisher
        acks: Union[Literal[0, 1, -1, "all"], object] = _missing,
        key_serializer: Optional[Callable[[Any], bytes]] = None,
        value_serializer: Optional[Callable[[Any], bytes]] = None,
        compression_type: Optional[Literal["gzip", "snappy", "lz4", "zstd"]] = None,
        max_batch_size: int = 16384,
        partitioner: Callable[
            [bytes, List[Partition], List[Partition]],
            Partition,
        ] = DefaultPartitioner(),
        max_request_size: int = 1048576,
        linger_ms: int = 0,
        send_backoff_ms: int = 100,
        ssl_context: Optional[SSLContext] = None,
        enable_idempotence: bool = False,
        transactional_id: Optional[str] = None,
        transaction_timeout_ms: int = 60000,
    ) -> AIOKafkaConsumer: ...
    async def _connect(self, *args: Any, **kwargs: Any) -> AIOKafkaConsumer: ...
    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None: ...
    def handle(  # type: ignore[override]
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
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[ConsumerRecord] = None,
        parse_message: AsyncParser[ConsumerRecord] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]],
    ]: ...
    @staticmethod
    async def _parse_message(
        message: ConsumerRecord,
    ) -> KafkaMessage: ...
    async def publish(  # type: ignore[override]
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
    ) -> Optional[DecodedMessage]: ...
    async def publish_batch(
        self,
        *msgs: SendableMessage,
        topic: str,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None: ...
    def _get_log_context(  # type: ignore[override]
        self,
        message: Optional[KafkaMessage],
        topics: Sequence[str] = (),
    ) -> Dict[str, Any]: ...
    def _process_message(
        self,
        func: Callable[[KafkaMessage], Awaitable[T_HandlerReturn]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[KafkaMessage], Awaitable[T_HandlerReturn]]: ...
