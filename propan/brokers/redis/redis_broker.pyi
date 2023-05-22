import logging
from typing import Any, Callable, Dict, List, Mapping, Optional, Type, TypeVar, Union

from redis.asyncio.client import Redis
from redis.asyncio.connection import BaseParser, Connection, DefaultParser, Encoder

from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.redis.schemas import Handler
from propan.log import access_logger
from propan.types import DecodedMessage, HandlerWrapper, SendableMessage

T = TypeVar("T")

class RedisBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Redis[bytes]
    __max_channel_len: int

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        polling_interval: float = 1.0,
        *,
        connection_class: Type[Connection] = Connection,
        max_connections: Optional[int] = None,
        host: str = "localhost",
        port: Union[str, int] = 6379,
        db: Union[str, int] = 0,
        password: Optional[str] = None,
        socket_timeout: Optional[float] = None,
        socket_connect_timeout: Optional[float] = None,
        socket_keepalive: bool = False,
        socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None,
        socket_type: int = 0,
        retry_on_timeout: bool = False,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        parser_class: Type[BaseParser] = DefaultParser,
        socket_read_size: int = 65536,
        health_check_interval: float = 0,
        client_name: Optional[str] = None,
        username: Optional[str] = None,
        encoder_class: Type[Encoder] = Encoder,
        # broker kwargs
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
    ) -> None: ...
    async def _connect(
        self,
        url: str = "redis://localhost:6379",
        host: str = "localhost",
        port: Union[str, int] = 6379,
        db: Union[str, int] = 0,
        password: Optional[str] = None,
        socket_timeout: Optional[float] = None,
        socket_connect_timeout: Optional[float] = None,
        socket_keepalive: bool = False,
        socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None,
        socket_type: int = 0,
        retry_on_timeout: bool = False,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        parser_class: Type[BaseParser] = DefaultParser,
        socket_read_size: int = 65536,
        health_check_interval: float = 0,
        client_name: Optional[str] = None,
        username: Optional[str] = None,
        encoder_class: Type[Encoder] = Encoder,
    ) -> Redis[bytes]: ...
    async def close(self) -> None: ...
    @staticmethod
    async def _parse_message(message: Any) -> PropanMessage: ...
    def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]: ...
    def handle(  # type: ignore[override]
        self,
        channel: str,
        *,
        pattern: bool = False,
    ) -> HandlerWrapper: ...
    def _get_log_context(  # type: ignore[override]
        self, message: PropanMessage, channel: str
    ) -> Dict[str, Any]: ...
    @staticmethod
    async def _decode_message(message: PropanMessage) -> DecodedMessage: ...
    @property
    def fmt(self) -> str: ...
    async def start(self) -> None: ...
    async def publish(  # type: ignore[override]
        self,
        message: SendableMessage = "",
        channel: str = "",
        *,
        reply_to: str = "",
        headers: Optional[Dict[str, Any]] = None,
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> None: ...
