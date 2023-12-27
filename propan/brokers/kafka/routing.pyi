from typing import Any, Awaitable, Callable, Optional, Sequence, Union

from aiokafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from aiokafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from aiokafka.structs import ConsumerRecord
from fast_depends.dependencies import Depends
from typing_extensions import Literal

from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.routing import BrokerRouter

class KafkaRouter(BrokerRouter[ConsumerRecord]):
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
