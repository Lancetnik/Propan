from ssl import SSLContext
from logging import Logger
from typing import Union, Optional, Callable
from yarl import URL

import aio_pika
from pamqp.common import FieldTable

from propan.log import access_logger
from propan.brokers.model import BrokerUsecase

from .schemas import RabbitExchange, RabbitQueue


class RabbitBroker(BrokerUsecase):
    async def __init__(self,
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
                       logger: Optional[Logger] = access_logger,
                       apply_types: bool = True,
                       consumers: Optional[int] = None):
        '''
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
        '''
        ...

    async def connect(self,
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
                      client_properties: Optional[FieldTable] = None):
        '''
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
        '''
        ...

    async def publish_message(self,
                              message: Union[aio_pika.Message, str, dict],
                              queue: Union[RabbitQueue, str] = "",
                              exchange: Union[RabbitExchange, str, None] = None,
                              mandatory: bool = True,
                              immediate: bool = False,
                              timeout: aio_pika.abc.TimeoutType = None) -> None:
        ...

    def handle(self,
               queue: Union[str, RabbitQueue],
               exchange: Union[str, RabbitExchange, None] = None,
               retry: Union[bool, int] = False) -> Callable:
        '''
        retry: Union[bool, int] - at exeption message will returns to queue `int` times or endless if `True`
        '''
        ...

    async def __aenter__(self) -> 'RabbitBroker':
        ...
