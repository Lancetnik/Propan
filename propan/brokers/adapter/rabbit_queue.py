import asyncio
from functools import wraps
from typing import Callable, Dict, Optional

import aio_pika
from pydantic.error_wrappers import ValidationError

from propan.config import settings

from propan.logger import loguru
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
        *args,
        logger: LoggerUsecase = EmptyLogger(),
        connection_data: Optional[ConnectionData] = None,
        consumers: Optional[int] = None,
        **kwargs
    ):
        self.logger = logger

        if connection_data is not None:
            kwargs = connection_data.dict()

        self._connection_args = args
        self._connecttion_kwargs = kwargs
        self._max_consumers = consumers

    async def connect(self, *args, **kwargs) -> aio_pika.Connection:
        try:
            if settings.IS_CONFIGURED is False:
                raise ValueError()

            _args = tuple()
            _kwargs = ConnectionData(
                host = settings.RABBIT_HOST,
                port = settings.RABBIT_PORT,
                login = settings.RABBIT_LOGIN,
                password = settings.RABBIT_PASSWORD,
                virtualhost = settings.RABBIT_VHOST
            ).dict()

        except (ValidationError, ValueError) as e:
            _args = args or self._connection_args
            _kwargs = kwargs or self._connecttion_kwargs
            if isinstance(e, ValidationError):
                self.logger.info(f"Using params: args={_args}, kwargs={_kwargs}")

        try:
            if _args or _kwargs:
                self._connection = await aio_pika.connect_robust(*_args, **_kwargs)
            else:
                self._connection = await aio_pika.connect_robust()
        except Exception as e:
            loguru.error(e)
            if self.logger is not loguru:
                self.logger.error(e)
            exit()

        return self._connection

    async def init_channel(self, max_consumers: Optional[int] = None) -> None:
        max_consumers = settings.MAX_CONSUMERS or max_consumers or self._max_consumers
        self._channel = await self._connection.channel()
        if max_consumers:
            self.logger.info(f"Set max consumers to {max_consumers}")
            await self._channel.set_qos(prefetch_count=int(max_consumers))

    async def start(self):
        for queue_name in self.handlers.keys():
            queue = await self._channel.declare_queue(queue_name)
            self.logger.success(
                f'[*] Waiting for messages in {queue_name}. To exit press CTRL+C')
            await queue.consume(self.handle_message)

    async def publish_message(self, queue_name: str, message: str, *args, **kwargs) -> None:
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=str(message).encode(),
                *args, **kwargs
            ),
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
