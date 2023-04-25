import logging
from ssl import SSLContext
from typing import Any, Dict, List, Optional, Union

import aio_pika
import aiormq
from pamqp.common import FieldTable
from pydantic import BaseModel
from yarl import URL

from propan.brokers.model import BrokerUsecase
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, DecoratedCallable, Wrapper

class RabbitBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]

    __max_queue_len: int
    __max_exchange_len: int

    def __init__(
        self,
        url: Union[str, URL, None] = None,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
        ssl: bool = False,
        ssl_options: Optional[aio_pika.abc.SSLOptions] = None,
        ssl_context: Optional[SSLContext] = None,
        timeout: aio_pika.abc.TimeoutType = None,
        client_properties: Optional[FieldTable] = None,
        *,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        consumers: Optional[int] = None,
    ) -> None:
        """
        URL string might be contain ssl parameters e.g.
        `amqps://user:pass@host//?ca_certs=ca.pem&certfile=crt.pem&keyfile=key.pem`

        :param client_properties: add custom client capability.
        :param url:
            RFC3986_ formatted broker address. When :class:`None`
            will be used keyword arguments.
        :param host: hostname of the broker
        :param port: broker port 5672 by default
        :param login: username string. `'guest'` by default.
        :param password: password string. `'guest'` by default.
        :param virtualhost: virtualhost parameter. `'/'` by default
        :param ssl: use SSL for connection. Should be used with addition kwargs.
        :param ssl_options: A dict of values for the SSL connection.
        :param timeout: connection timeout in seconds
        :param ssl_context: ssl.SSLContext instance

        .. _RFC3986: https://goo.gl/MzgYAs
        .. _official Python documentation: https://goo.gl/pty9xA
        """
        ...
    async def connect(
        self,
        url: Union[str, URL, None] = None,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
        ssl: bool = False,
        ssl_options: Optional[aio_pika.abc.SSLOptions] = None,
        ssl_context: Optional[SSLContext] = None,
        timeout: aio_pika.abc.TimeoutType = None,
        client_properties: Optional[FieldTable] = None,
    ) -> aio_pika.Connection:
        """
        URL string might be contain ssl parameters e.g.
        `amqps://user:pass@host//?ca_certs=ca.pem&certfile=crt.pem&keyfile=key.pem`

        :param client_properties: add custom client capability.
        :param url:
            RFC3986_ formatted broker address. When :class:`None`
            will be used keyword arguments.
        :param host: hostname of the broker
        :param port: broker port 5672 by default
        :param login: username string. `'guest'` by default.
        :param password: password string. `'guest'` by default.
        :param virtualhost: virtualhost parameter. `'/'` by default
        :param ssl: use SSL for connection. Should be used with addition kwargs.
        :param ssl_options: A dict of values for the SSL connection.
        :param timeout: connection timeout in seconds
        :param ssl_context: ssl.SSLContext instance

        .. _RFC3986: https://goo.gl/MzgYAs
        .. _official Python documentation: https://goo.gl/pty9xA
        """
        ...
    async def publish(  # type: ignore[override]
        self,
        message: Union[aio_pika.Message, str, Dict[str, Any], BaseModel] = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        # publish kwargs
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: aio_pika.abc.TimeoutType = None,
        # callback kwargs
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        # message kwargs
        headers: Optional[aio_pika.abc.HeadersType] = None,
        content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        delivery_mode: Union[aio_pika.abc.DeliveryMode, int, None] = None,
        priority: Optional[int] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        expiration: Optional[aio_pika.abc.DateType] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[aio_pika.abc.DateType] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> Optional[aiormq.abc.ConfirmationFrameType]: ...
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        retry: Union[bool, int] = False,
    ) -> Wrapper:
        """
        retry: Union[bool, int] - at exeption message will returns to queue `int` times or endless if `True`
        """
        ...
    async def __aenter__(self) -> "RabbitBroker": ...
    async def _connect(self, *args: Any, **kwargs: Any) -> aio_pika.Connection: ...
    async def close(self) -> None: ...
    @staticmethod
    async def _decode_message(
        message: aio_pika.IncomingMessage,
    ) -> DecodedMessage: ...
    @staticmethod
    def _process_message(
        func: DecoratedCallable, watcher: Optional[BaseWatcher] = None
    ) -> DecoratedCallable: ...
    def _get_log_context(  # type: ignore[override]
        self,
        message: Optional[aio_pika.Message],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
        **kwrags: AnyDict,
    ) -> Dict[str, Any]: ...
    async def _init_channel(self, max_consumers: Optional[int] = None) -> None: ...
    async def _init_handler(
        self, handler: Handler
    ) -> aio_pika.abc.AbstractRobustQueue: ...
    async def _init_queue(
        self, queue: RabbitQueue
    ) -> aio_pika.abc.AbstractRobustQueue: ...
    async def _init_exchange(
        self, exchange: RabbitExchange
    ) -> aio_pika.abc.AbstractRobustExchange: ...
    async def start(self) -> None: ...
