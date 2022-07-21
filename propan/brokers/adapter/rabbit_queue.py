import asyncio
from functools import wraps
from typing import Callable, Dict, Optional

import aio_pika

from propan.config import settings

from propan.logger.model.usecase import LoggerUsecase
from propan.logger.adapter.empty import EmptyLogger

from propan.brokers.model.bus_connection import ConnectionData
from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.brokers.push_back_watcher import PushBackWatcher


class AsyncRabbitQueueAdapter(BrokerUsecase):
    logger: LoggerUsecase
    _connection: aio_pika.RobustConnection
    _channel: aio_pika.RobustChannel

    def __init__(
        self,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
        vhost: Optional[str] = None,
        logger: LoggerUsecase = EmptyLogger(),
        connection_data: Optional[ConnectionData] = None,
        consumers=10,
    ):
        self.logger = logger
        self.connection_data = connection_data or ConnectionData(
            host or settings.RABBIT_HOST if settings.IS_CONFIGURED else "localhost",
            port or settings.RABBIT_PORT if settings.IS_CONFIGURED else 5672,
            login or settings.RABBIT_LOGIN if settings.IS_CONFIGURED else None,
            password or settings.RABBIT_PASSWORD if settings.IS_CONFIGURED else None,
            vhost or settings.RABBIT_VHOST if settings.IS_CONFIGURED else "/"
        )
        self._url = url
        self._max_consumers = consumers or settings.MAX_CONSUMERS

    async def connect(self) -> aio_pika.Connection:
        if self._url:
            self._connection = await aio_pika.connect_robust(
                url=self._url
            )
        else:
            self._connection = await aio_pika.connect_robust(
                host=self.connection_data.host,
                port=self.connection_data.port,
                login=self.connection_data.login,
                password=self.connection_data.password,
                virtualhost=self.connection_data.virtualhost,
            )
        return self._connection

    async def init_channel(self, max_consumers = None) -> None:
        self._channel = await self._connection.channel()
        if max_consumers:
            await self._channel.set_qos(prefetch_count=max_consumers)
    
    async def start(self):
        for queue_name in self.handlers.keys():
            queue = await self._channel.declare_queue(queue_name)
            self.logger.success(f'[*] Waiting for messages in {queue_name}. To exit press CTRL+C')
            await queue.consume(self.handle_message)

    async def publish_message(self, queue_name: str, message: str) -> None:
        await self._channel.default_exchange.publish(
            aio_pika.Message(str(message).encode()),
            routing_key=queue_name,
        )

    async def handle_message(self, message: aio_pika.IncomingMessage) -> None:
        queue_name = message.routing_key
        body = message.body.decode()
        async with message.process():
            self.logger.info(f"[x] Received {body} in {queue_name}")
            await self.handlers[queue_name](body)

    async def close(self):
        await self._connection.close()

    def retry(self, queue_name, try_number=3):
        watcher = PushBackWatcher(try_number)

        def decorator(func):
            @wraps(func)
            async def wrapper(message):
                try:
                    response = await func(message)

                except Exception as e:
                    watcher.add(message)
                    if not watcher.is_max(message):
                        self.logger.error(
                            f'In "{message}" error is occured. Pushing back it to rabbit.')
                        await self.publish_message(queue_name, message)
                    else:
                        self.logger.error(
                            f'"{message}" already retried {watcher.max_tries} times. Skipped.')
                        watcher.remove(message)
                    raise e

                else:
                    watcher.remove(message)
                    return response
            return wrapper
        return decorator
