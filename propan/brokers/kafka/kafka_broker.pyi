from asyncio import AbstractEventLoop
from ssl import SSLContext
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.abc import AbstractTokenProvider
from aiokafka.producer.producer import _missing
from aiokafka.structs import ConsumerRecord
from kafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from kafka.partitioner.default import DefaultPartitioner
from typing_extensions import Literal, TypeVar

from propan.__about__ import __version__
from propan.brokers.kafka.schemas import Handler
from propan.brokers.model.broker_usecase import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import SendableMessage, Wrapper

T = TypeVar("T")
Partition = TypeVar("Partition")

class KafkaBroker(BrokerUsecase):
    _publisher: Optional[AIOKafkaProducer]
    _connection: Callable[[Tuple[str, ...]], AIOKafkaConsumer]
    __max_topic_len: int
    handlers: List[Handler]

    def __init__(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
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
        # broker
        log_fmt: Optional[str] = None,
    ) -> None: ...
    async def connect(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
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
    async def close(self) -> None: ...
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
    ) -> Wrapper: ...
    async def start(self) -> None: ...
    @staticmethod
    async def _parse_message(message: ConsumerRecord) -> PropanMessage: ...
    def _process_message(
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
    ) -> Callable[[PropanMessage], T]: ...
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
        callback_timeout: float | None = None,
        raise_timeout: bool = False,
    ) -> Any: ...
    @property
    def fmt(self) -> str: ...
    def _get_log_context(  # type: ignore[override]
        self,
        message: PropanMessage,
        topics: Sequence[str] = (),
    ) -> Dict[str, Any]: ...
