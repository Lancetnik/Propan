import logging
import ssl
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from fast_depends.dependencies import Depends
from nats.aio.client import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_DRAIN_TIMEOUT,
    DEFAULT_INBOX_PREFIX,
    DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
    DEFAULT_MAX_OUTSTANDING_PINGS,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_PENDING_SIZE,
    DEFAULT_PING_INTERVAL,
    DEFAULT_RECONNECT_TIME_WAIT,
    Callback,
    Client,
    Credentials,
    ErrorCallback,
    JWTCallback,
    SignatureCallback,
)
from nats.aio.msg import Msg
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.broker_usecase import CustomDecoder, CustomParser
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.log import access_logger
from propan.types import DecodedMessage, HandlerWrapper, SendableMessage

T = TypeVar("T")
NatsMessage: TypeAlias = PropanMessage[Msg]

class NatsBroker(BrokerUsecase[Msg, Client]):
    logger: logging.Logger
    handlers: List[Handler]

    def __init__(
        self,
        servers: Union[str, List[str]] = ["nats://localhost:4222"],  # noqa: B006
        *,
        error_cb: Optional[ErrorCallback] = None,
        disconnected_cb: Optional[Callback] = None,
        closed_cb: Optional[Callback] = None,
        discovered_server_cb: Optional[Callback] = None,
        reconnected_cb: Optional[Callback] = None,
        name: Optional[str] = None,
        pedantic: bool = False,
        verbose: bool = False,
        allow_reconnect: bool = True,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
        reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT,
        max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS,
        ping_interval: int = DEFAULT_PING_INTERVAL,
        max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS,
        dont_randomize: bool = False,
        flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
        no_echo: bool = False,
        tls: Optional[ssl.SSLContext] = None,
        tls_hostname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        drain_timeout: int = DEFAULT_DRAIN_TIMEOUT,
        signature_cb: Optional[SignatureCallback] = None,
        user_jwt_cb: Optional[JWTCallback] = None,
        user_credentials: Optional[Credentials] = None,
        nkeys_seed: Optional[str] = None,
        inbox_prefix: Union[str, bytes] = DEFAULT_INBOX_PREFIX,
        pending_size: int = DEFAULT_PENDING_SIZE,
        flush_timeout: Optional[float] = None,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[Msg] = None,
        parse_message: CustomParser[Msg] = None,
        protocol: str = "nats",
    ) -> None: ...
    async def connect(
        self,
        *,
        servers: Union[str, List[str]] = ["nats://localhost:4222"],  # noqa: B006
        error_cb: Optional[ErrorCallback] = None,
        disconnected_cb: Optional[Callback] = None,
        closed_cb: Optional[Callback] = None,
        discovered_server_cb: Optional[Callback] = None,
        reconnected_cb: Optional[Callback] = None,
        name: Optional[str] = None,
        pedantic: bool = False,
        verbose: bool = False,
        allow_reconnect: bool = True,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
        reconnect_time_wait: int = DEFAULT_RECONNECT_TIME_WAIT,
        max_reconnect_attempts: int = DEFAULT_MAX_RECONNECT_ATTEMPTS,
        ping_interval: int = DEFAULT_PING_INTERVAL,
        max_outstanding_pings: int = DEFAULT_MAX_OUTSTANDING_PINGS,
        dont_randomize: bool = False,
        flusher_queue_size: int = DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
        no_echo: bool = False,
        tls: Optional[ssl.SSLContext] = None,
        tls_hostname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        drain_timeout: int = DEFAULT_DRAIN_TIMEOUT,
        signature_cb: Optional[SignatureCallback] = None,
        user_jwt_cb: Optional[JWTCallback] = None,
        user_credentials: Optional[Credentials] = None,
        nkeys_seed: Optional[str] = None,
        inbox_prefix: Union[str, bytes] = DEFAULT_INBOX_PREFIX,
        pending_size: int = DEFAULT_PENDING_SIZE,
        flush_timeout: Optional[float] = None,
    ) -> Client: ...
    async def publish(  # type: ignore[override]
        self,
        message: SendableMessage,
        subject: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> Optional[DecodedMessage]: ...
    def handle(  # type: ignore[override]
        self,
        subject: str,
        queue: str = "",
        *,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[Msg] = None,
        parse_message: CustomParser[Msg] = None,
        description: str = "",
    ) -> HandlerWrapper: ...
    def _get_log_context(  # type: ignore[override]
        self,
        message: Optional[NatsMessage],
        subject: str,
        queue: str = "",
    ) -> Dict[str, Any]: ...
    async def _connect(
        self,
        *,
        url: Optional[str] = None,
        error_cb: Optional[ErrorCallback] = None,
        reconnected_cb: Optional[Callback] = None,
        **kwargs: Any,
    ) -> Client: ...
    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None: ...
    async def _parse_message(self, message: Msg) -> NatsMessage: ...
    def _process_message(
        self,
        func: Callable[[NatsMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher] = None,
    ) -> Callable[[NatsMessage], Awaitable[T]]: ...
