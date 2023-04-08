import logging
from ssl import SSLContext
from typing import Any, Callable, Dict, Optional, Union

import aio_pika
import aiormq
from pamqp.common import FieldTable
from propan.brokers.model import BrokerUsecase
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.rabbit.schemas import RabbitExchange, RabbitQueue
from propan.log import access_logger
from propan.types import DecoratedCallable
from yarl import URL

class RabbitBroker(BrokerUsecase):
    async def __init__(
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
    ):
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
    async def publish_message(
        self,
        message: Union[aio_pika.Message, str, Dict[str, Any]],
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: aio_pika.abc.TimeoutType = None,
    ) -> Optional[aiormq.abc.ConfirmationFrameType]: ...
    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        retry: Union[bool, int] = False,
    ) -> Callable[[DecoratedCallable], None]:
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
    ) -> Union[str, Dict[str, Any]]: ...
    @staticmethod
    def _process_message(
        func: DecoratedCallable, watcher: Optional[BaseWatcher] = None
    ) -> DecoratedCallable: ...
    def _get_log_context(
        self,
        message: Optional[aio_pika.Message],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
        **kwrags,
    ) -> Dict[str, Any]: ...
