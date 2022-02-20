import asyncio
from functools import wraps
from typing import Callable, Dict

import aio_pika

from propan.config.lazy import settings

from propan.logger.model.usecase import LoggerUsecase
from propan.logger.adapter.empty import EmptyLogger

from propan.brokers.model.bus_connection import ConnectionData
from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.brokers.push_back_watcher import PushBackWatcher


class AsyncRabbitQueueAdapter(BrokerUsecase):
    logger: LoggerUsecase
    _connection: aio_pika.RobustConnection
    _channel: aio_pika.RobustChannel
    _process_message: Dict[str, Callable] = {}

    def __init__(
        self,
        host=None,
        login=None,
        password=None,
        virtualhost=None,
        logger: LoggerUsecase = EmptyLogger(),
        connection_data=None,
        consumers=None
    ):
        self.logger = logger
        self.connection_data = connection_data or ConnectionData(
            host or settings.RABBIT_HOST, login or settings.RABBIT_LOGIN,
            password or settings.RABBIT_PASSWORD, virtualhost or settings.RABBIT_VHOST
        )
        self.connect()
        asyncio.get_event_loop().run_until_complete(
            self.init_channel(max_consumers=consumers or settings.MAX_CONSUMERS)
        )

    def connect(self) -> None:
        loop = asyncio.get_event_loop()
        self._connection = loop.run_until_complete(aio_pika.connect_robust(
            host=self.connection_data.host,
            login=self.connection_data.login,
            password=self.connection_data.password,
            virtualhost=self.connection_data.virtualhost,
            loop=loop
        ))

    async def init_channel(self, max_consumers: int = None) -> None:
        self._channel = await self._connection.channel()
        if max_consumers:
            await self._channel.set_qos(prefetch_count=max_consumers)

    async def set_queue_handler(
        self, queue_name: str,
        handler: Callable, retrying_on_error: bool = False
    ) -> None:
        queue = await self._channel.declare_queue(queue_name)
        self._process_message[queue_name] = handler
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
            await self._process_message[queue_name](body)

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
