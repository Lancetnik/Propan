from ssl import SSLContext
from typing import Union, Optional, Callable
from yarl import URL

import aio_pika
from pamqp.common import FieldTable

from propan.logger import empty
from propan.logger.model.usecase import LoggerUsecase
from propan.brokers.model import BrokerUsecase, ConnectionData

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
                       logger: LoggerUsecase = empty,
                       connection_data: Optional[ConnectionData] = None,
                       consumers: Optional[int] = None):
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
        ...

    async def publish_message(self,
                              message: Union[aio_pika.Message, str, dict],
                              queue: str = "",
                              exchange: Union[RabbitExchange, str, None] = None,
                              mandatory: bool = True,
                              immediate: bool = False,
                              timeout: aio_pika.abc.TimeoutType = None) -> None:
        ...

    def set_handler(self,
                    queue: Union[str, RabbitQueue],
                    func: Callable,
                    exchange: Union[RabbitExchange, None, str] = None) -> None:
        ...


def retry_proccess(try_number: int = None, logger: LoggerUsecase = empty) -> Callable:
    ...
