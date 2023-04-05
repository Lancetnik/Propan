import ssl
from logging import Logger
from typing import (
    Callable,
    List,
    Dict,
    Optional,
    Union,
)

from nats.aio.client import (
    Client,
    Callback,
    ErrorCallback,
    SignatureCallback,
    JWTCallback,
    Credentials,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_RECONNECT_TIME_WAIT,
    DEFAULT_MAX_RECONNECT_ATTEMPTS,
    DEFAULT_PING_INTERVAL,
    DEFAULT_MAX_OUTSTANDING_PINGS,
    DEFAULT_MAX_FLUSHER_QUEUE_SIZE,
    DEFAULT_DRAIN_TIMEOUT,
    DEFAULT_INBOX_PREFIX,
    DEFAULT_PENDING_SIZE,
)

from propan.log import access_logger
from propan.brokers.model import BrokerUsecase

from propan.brokers.nats.schemas import Handler


class NatsBroker(BrokerUsecase):
    logger: Logger
    handlers: List[Handler] = []
    _connection: Optional[Client] = None

    __max_queue_len = 4

    def __init__(
        self,
        servers: Union[str, List[str]] = ["nats://localhost:4222"],
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
        *,
        logger: Optional[Logger] = access_logger,
        apply_types: bool = True,
        consumers: Optional[int] = None,
    ):
        ...

    async def connect(
        self,
        servers: Union[str, List[str]] = ["nats://localhost:4222"],
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
        flush_timeout: Optional[float] = None) -> Client:
        ...

    async def publish_message(self,
                              message: Union[str, dict],
                              subject: str,
                              reply: str = '',
                              headers: Optional[Dict[str, str]] = None) -> None:
        ...
    
    def handle(self,
               subject: str,
               queue: str = "",
               retry: Union[bool, int] = False) -> Callable:
        ...

    async def __aenter__(self) -> 'NatsBroker':
        ...