import logging
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from fast_depends.dependencies import Depends
from redis.asyncio.client import Redis
from redis.asyncio.connection import BaseParser, Connection, DefaultParser, Encoder
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.middlewares import BaseMiddleware
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.redis.schemas import Handler
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, SendableMessage

T = TypeVar("T")
RedisMessage: TypeAlias = PropanMessage[AnyDict]

class RedisBroker(BrokerAsyncUsecase[AnyDict, Redis[bytes]]):
    handlers: List[Handler]
    middlewares: Sequence[Type[BaseMiddleware[AnyDict]]]
    __max_channel_len: int

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        *,
        polling_interval: float = 1.0,
        host: str = "localhost",
        port: Union[str, int] = 6379,
        username: Optional[str] = None,
        password: Optional[str] = None,
        db: Union[str, int] = 0,
        client_name: Optional[str] = None,
        health_check_interval: float = 0,
        max_connections: Optional[int] = None,
        socket_timeout: Optional[float] = None,
        socket_connect_timeout: Optional[float] = None,
        socket_read_size: int = 65536,
        socket_keepalive: bool = False,
        socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None,
        socket_type: int = 0,
        retry_on_timeout: bool = False,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        parser_class: Type[BaseParser] = DefaultParser,
        connection_class: Type[Connection] = Connection,
        encoder_class: Type[Encoder] = Encoder,
        # broker kwargs
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        dependencies: Sequence[Depends] = (),
        middlewares: Sequence[Type[BaseMiddleware[AnyDict]]] = (),
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        protocol: str = "redis",
    ) -> None:
        """Redis Pub/sub Propan broker

        URL examples:

        - redis://[[username]:[password]]@localhost:6379/0
        - rediss://[[username]:[password]]@localhost:6379/0
        - unix://[username@]/path/to/socket.sock?db=0[&password=password]

        Three URL schemes are supported:

        - `redis://` creates a TCP socket connection. See more at:
          <https://www.iana.org/assignments/uri-schemes/prov/redis>
        - `rediss://` creates a SSL wrapped TCP socket connection. See more at:
          <https://www.iana.org/assignments/uri-schemes/prov/rediss>
        - `unix://`: creates a Unix Domain Socket connection.

        Url will be parsed to kwargs and partially replaced by keywords arguments if they specified.
        """
    async def connect(
        self,
        *,
        url: str = "redis://localhost:6379",
        host: str = "localhost",
        port: Union[str, int] = 6379,
        username: Optional[str] = None,
        password: Optional[str] = None,
        db: Union[str, int] = 0,
        client_name: Optional[str] = None,
        health_check_interval: float = 0,
        max_connections: Optional[int] = None,
        socket_timeout: Optional[float] = None,
        socket_connect_timeout: Optional[float] = None,
        socket_read_size: int = 65536,
        socket_keepalive: bool = False,
        socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None,
        socket_type: int = 0,
        retry_on_timeout: bool = False,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        parser_class: Type[BaseParser] = DefaultParser,
        connection_class: Type[Connection] = Connection,
        encoder_class: Type[Encoder] = Encoder,
    ) -> Redis[bytes]:
        """Connect to Redis

        URL examples:

        - redis://[[username]:[password]]@localhost:6379/0
        - rediss://[[username]:[password]]@localhost:6379/0
        - unix://[username@]/path/to/socket.sock?db=0[&password=password]

        Three URL schemes are supported:

        - `redis://` creates a TCP socket connection. See more at:
          <https://www.iana.org/assignments/uri-schemes/prov/redis>
        - `rediss://` creates a SSL wrapped TCP socket connection. See more at:
          <https://www.iana.org/assignments/uri-schemes/prov/rediss>
        - `unix://`: creates a Unix Domain Socket connection.

        Url will be parsed to kwargs and partially replaced by keywords arguments if they specified.
        """
    async def _connect(self, *args: Any, **kwargs: Any) -> Redis[bytes]: ...
    async def start(self) -> None:
        """Initialize Redis connection and startup all consumers"""
    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        """Cancel all consumers tasks and subscribtions, close Redis connection"""
    def handle(  # type: ignore[override]
        self,
        channel: str,
        *,
        pattern: bool = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]:
        """Register channel consumer method

        Args:
            channel: channel to consume messages
            pattern: use psubscribe or subscribe method
            dependencies: wrap handler dependencies
            decode_message: custom PropanMessage[AnyDict] decoder
            parse_message: custom redis message to PropanMessage[AnyDict] parser
            description: AsyncAPI channel object description

        Returns:
            Async or sync function decorator
        """
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
    ) -> Optional[DecodedMessage]:
        """Publish the message to the channel.

        Args:
            message: encodable message to send
            channel: channel to publish message
            reply_to: queue to send response
            headers: message headers (for consumers)
            callback: wait for response
            callback_timeout: response waiting time
            raise_timeout: if False timeout returns None instead TimeoutError

        Returns:
            `None` if you are not waiting for response
            (reply_to and callback are not specified)

            `DecodedMessage` | `None` if response is expected
        """
    def _get_log_context(  # type: ignore[override]
        self, message: Optional[RedisMessage], channel: str
    ) -> Dict[str, Any]: ...
    @staticmethod
    async def _decode_message(message: RedisMessage) -> DecodedMessage: ...
    @staticmethod
    async def _parse_message(message: AnyDict) -> RedisMessage: ...
    def _process_message(
        self,
        func: Callable[[RedisMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[RedisMessage], Awaitable[T]]: ...
