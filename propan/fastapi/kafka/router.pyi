import logging
from asyncio import AbstractEventLoop
from enum import Enum
from ssl import SSLContext
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Type, Union

from aiokafka.abc import AbstractTokenProvider
from aiokafka.coordinator.assignors.abstract import AbstractPartitionAssignor
from aiokafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from aiokafka.producer.producer import _missing
from aiokafka.structs import ConsumerRecord
from fastapi import params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from kafka.partitioner.default import DefaultPartitioner
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
from typing_extensions import Literal, TypeVar

from propan import KafkaBroker
from propan.__about__ import __version__
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.fastapi.core import PropanRouter
from propan.log import access_logger

Partition = TypeVar("Partition")

class KafkaRouter(PropanRouter[KafkaBroker]):
    def __init__(
        self,
        bootstrap_servers: Union[str, List[str]] = "localhost",
        *,
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
        # FastAPI kwargs
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[routing.BaseRoute]] = None,
        routes: Optional[List[routing.BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[APIRoute] = APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(
            generate_unique_id
        ),
        loop: Optional[AbstractEventLoop] = None,
        # Broker kwargs
        schema_url: str = "/asyncapi",
        setup_state: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        decode_message: AsyncDecoder[ConsumerRecord] = None,
        parse_message: AsyncParser[ConsumerRecord] = None,
        protocol: str = "kafka",
    ) -> None:
        pass
    def add_api_mq_route(  # type: ignore[override]
        self,
        *topics: str,
        endpoint: HandlerCallable[T_HandlerReturn],
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
        # broker kwargs
        retry: Union[bool, int] = False,
        decode_message: AsyncDecoder[ConsumerRecord] = None,
        parse_message: AsyncParser[ConsumerRecord] = None,
        description: str = "",
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]]:
        pass
    def event(  # type: ignore[override]
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
        # broker kwargs
        dependencies: Optional[Sequence[params.Depends]] = None,
        retry: Union[bool, int] = False,
        decode_message: AsyncDecoder[ConsumerRecord] = None,
        parse_message: AsyncParser[ConsumerRecord] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]],
    ]: ...
