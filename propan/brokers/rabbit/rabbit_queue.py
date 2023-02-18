import asyncio
import os
from functools import wraps, lru_cache
from time import monotonic
from typing import Optional, Callable, Union, List
import json

import aio_pika
from pydantic.error_wrappers import ValidationError

from propan.config import settings

from propan.logger import loguru, empty
from propan.logger.model.usecase import LoggerUsecase

from propan.brokers.model import BrokerUsecase, ConnectionData
from propan.brokers.push_back_watcher import PushBackWatcher

from .schemas import RabbitQueue, RabbitExchange, Handler


class RabbitBroker(BrokerUsecase):
    logger: LoggerUsecase
    handlers: List[Handler] = []
    _connection: aio_pika.RobustConnection
    _channel: aio_pika.RobustChannel

    def __init__(
        self,
        *args,
        logger: LoggerUsecase = empty,
        connection_data: Optional[ConnectionData] = None,
        consumers: Optional[int] = None,
        **kwargs
    ):
        self.logger = logger

        if connection_data is not None:
            kwargs = connection_data.dict()

        self._connection_args = args
        self._connection_kwargs = kwargs
        self._max_consumers = consumers

    async def connect(self, *args, **kwargs) -> aio_pika.Connection:
        try:
            if settings.IS_CONFIGURED is False:
                raise ValueError()

            _args = tuple()
            _kwargs = ConnectionData(
                host=settings.RABBIT_HOST,
                port=settings.RABBIT_PORT,
                login=settings.RABBIT_LOGIN,
                password=settings.RABBIT_PASSWORD,
                virtualhost=settings.RABBIT_VHOST
            ).dict()

        except (ValidationError, ValueError) as e:
            _args = args or self._connection_args
            _kwargs = kwargs or self._connection_kwargs
            if isinstance(e, ValidationError):
                self.logger.info(
                    f"Using params: args={_args}, kwargs={_kwargs}")

        else:
            _kwargs = {
                **(kwargs or self._connection_kwargs),
                **_kwargs
            }

        try:
            if _args or _kwargs:
                self._connection = await aio_pika.connect_robust(
                    *_args, **_kwargs, loop=asyncio.get_event_loop()
                )
            else:
                self._connection = await aio_pika.connect_robust(
                    loop=asyncio.get_event_loop()
                )

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

    def set_handler(self,
                    queue: Union[str, RabbitQueue],
                    func: Callable,
                    exchange: Union[RabbitExchange, None, str] = None) -> None:
        if isinstance(queue, str):
            queue = RabbitQueue(name=queue)
        elif not isinstance(queue, RabbitQueue):
            raise ValueError(f"Queue '{queue}' should be 'str' | 'RabbitQueue' instance")

        if exchange is not None:
            if isinstance(exchange, str):
                exchange = RabbitExchange(name=exchange)
            elif not isinstance(exchange, RabbitExchange):
                raise ValueError(f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance")

        handler = Handler(callback=func, queue=queue, exchange=exchange)
        self.handlers.append(handler)

    async def start(self):
        for handler in self.handlers:
            queue = await self._init_handler(handler)

            func = handler.callback
            func = _rabbit_decode(func)
            if self.logger is not empty:
                func = _log_execution(handler.queue.name, self.logger)(func)

            self.logger.success(
                '[*] Waiting for messages in '
                f'`{handler.exchange.name if handler.exchange else "default"}` exchange with '
                f'`{handler.queue.name}` queue PID {os.getpid()}. '
                'To exit press CTRL+C'
            )

            await queue.consume(func)

    async def publish_message(self,
                              message: Union[aio_pika.Message, str, dict],
                              queue: str = "",
                              exchange: Union[RabbitExchange, str, None] = None,
                              **publish_args) -> None:
        if not isinstance(message, aio_pika.Message):
            if isinstance(message, dict):
                message = aio_pika.Message(json.dumps(message).encode(), content_type="application/json")
            else:
                message = aio_pika.Message(message.encode(), content_type="text/plain")

        if exchange is not None:
            if isinstance(exchange, str):
                exchange = RabbitExchange(name=exchange)
            elif not isinstance(exchange, RabbitExchange):
                raise ValueError(f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance")

        if exchange is None:
            exchange_obj = self._channel.default_exchange
        else:
            exchange_obj = await self._channel.get_exchange(exchange.name)

        return await exchange_obj.publish(
            message=message,
            routing_key=queue,
            **publish_args,
        )

    async def close(self):
        await self._connection.close()

    async def _init_handler(self, handler: Handler):
        queue = await self._channel.declare_queue(**handler.queue.dict())
        if handler.exchange is not None:
            exchange = await self._channel.declare_exchange(**handler.exchange.dict())
            await queue.bind(exchange)
        return queue

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


def _rabbit_decode(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(message: aio_pika.IncomingMessage) -> None:
        body = message.body.decode()

        if message.content_type == "application/json":
            body = json.loads(body)

        async with message.process():
            return await func(body)
    return wrapper


def _log_execution(queue_name, logger):
    def decor(func):
        @wraps(func)
        async def wrapper(message: aio_pika.IncomingMessage):
            start = monotonic()
            logger.info(
                f"Received {message.message_id} with "
                f"'{message.body.decode()}' in `{queue_name}` PID {os.getpid()}"
            )

            try:
                return await func(message)
            finally:
                logger.info(
                    f"{message.message_id} in `{queue_name}` PID {os.getpid()} "
                    f"processed in {monotonic() - start}"
                )
        return wrapper
    return decor
