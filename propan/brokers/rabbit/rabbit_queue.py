import asyncio
from functools import wraps, partial
from typing import Optional, Callable, Union, List
import json

import aio_pika

from propan.logger import empty
from propan.logger.model.usecase import LoggerUsecase

from propan.brokers.model import BrokerUsecase
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext

from propan.brokers.rabbit.schemas import RabbitQueue, RabbitExchange, Handler


class RabbitBroker(BrokerUsecase):
    logger: LoggerUsecase
    handlers: List[Handler] = []
    _connection: Optional[aio_pika.RobustConnection] = None
    _channel: Optional[aio_pika.RobustChannel] = None

    def __init__(
        self,
        *args,
        logger: LoggerUsecase = empty,
        apply_types: bool = True,
        consumers: Optional[int] = None,
        **kwargs
    ):
        self.logger = logger

        self._connection_args = args
        self._connection_kwargs = kwargs
        self._max_consumers = consumers
        self._is_apply_types = apply_types

    async def connect(self, *args, **kwargs) -> aio_pika.Connection:
        if self._connection is None:
            _args = args or self._connection_args
            _kwargs = kwargs or self._connection_kwargs

            try:
                self._connection = await aio_pika.connect_robust(
                    *_args, **_kwargs, loop=asyncio.get_event_loop()
                )

            except Exception as e:
                self.logger.error(e)
                exit()

            return self._connection

    async def init_channel(self, max_consumers: Optional[int] = None) -> None:
        if self._channel is None:
            if self._connection is None:
                raise ValueError("RabbitBroker not connected yet")

            max_consumers = max_consumers or self._max_consumers
            self._channel = await self._connection.channel()
            if max_consumers:
                self.logger.info(f"Set max consumers to {max_consumers}")
                await self._channel.set_qos(prefetch_count=int(max_consumers))

    def handle(self,
               queue: Union[str, RabbitQueue],
               exchange: Union[str, RabbitExchange, None] = None,
               retry: Union[bool, int] = False) -> Callable:
        if isinstance(queue, str):
            queue = RabbitQueue(name=queue)
        elif not isinstance(queue, RabbitQueue):
            raise ValueError(
                f"Queue '{queue}' should be 'str' | 'RabbitQueue' instance")

        if exchange is not None:
            if isinstance(exchange, str):
                exchange = RabbitExchange(name=exchange)
            elif not isinstance(exchange, RabbitExchange):
                raise ValueError(
                    f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance")

        parent = super()

        def wrapper(func) -> None:
            func = parent.handle(func, retry)
            handler = Handler(callback=func, queue=queue, exchange=exchange)
            self.handlers.append(handler)

        return wrapper

    async def start(self):
        await self.connect()
        await self.init_channel()

        for handler in self.handlers:
            queue = await self._init_handler(handler)

            func = handler.callback

            self.logger.info(
                '[*] Waiting for messages in '
                f'`{handler.exchange.name if handler.exchange else "default"}` exchange with '
                f'`{handler.queue.name}` queue.'
            )

            await queue.consume(func)

    async def publish_message(self,
                              message: Union[aio_pika.Message, str, dict],
                              queue: str = "",
                              exchange: Union[RabbitExchange, str, None] = None,
                              **publish_args) -> None:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")

        if not isinstance(message, aio_pika.Message):
            if isinstance(message, dict):
                message = aio_pika.Message(json.dumps(
                    message).encode(), content_type="application/json")
            else:
                message = aio_pika.Message(
                    message.encode(), content_type="text/plain")

        if exchange is not None:
            if isinstance(exchange, str):
                exchange = RabbitExchange(name=exchange)
            elif not isinstance(exchange, RabbitExchange):
                raise ValueError(
                    f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance")

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

    @staticmethod
    def _decode_message(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: aio_pika.IncomingMessage) -> None:
            body = message.body.decode()

            if message.content_type == "application/json":
                body = json.loads(body)

            return await func(body)
        return wrapper

    @staticmethod
    def _process_message(func: Callable, watcher: Optional[BaseWatcher] = None) -> Callable:
        @wraps(func)
        async def wrapper(message: aio_pika.Message):
            if watcher is None:
                context = message.process()
            else:
                context = WatcherContext(watcher, message.message_id,
                                         on_success=partial(message.ack),
                                         on_error=partial(message.reject, True),
                                         on_max=partial(message.reject, False))
            async with context:
                return await func(message)
        return wrapper
