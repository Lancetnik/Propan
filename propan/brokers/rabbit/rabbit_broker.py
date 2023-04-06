import asyncio
import json
from functools import partial, wraps
from typing import Any, Callable, Dict, List, Optional, Union

import aio_pika
import aiormq
from propan.brokers.model import BrokerUsecase
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.utils.context.main import log_context


class RabbitBroker(BrokerUsecase):
    handlers: List[Handler] = []
    _connection: Optional[aio_pika.RobustConnection] = None
    _channel: Optional[aio_pika.RobustChannel] = None

    __max_queue_len = 4
    __max_exchange_len = 4

    def __init__(
        self,
        *args: Any,
        consumers: Optional[int] = None,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._max_consumers = consumers
        self._fmt = log_fmt

    async def __aenter__(self) -> "RabbitBroker":
        await self.connect()
        await self.init_channel()
        return self

    async def _connect(self, *args: Any, **kwargs: Any) -> aio_pika.Connection:
        return await aio_pika.connect_robust(
            *args, **kwargs, loop=asyncio.get_event_loop()
        )

    async def init_channel(self, max_consumers: Optional[int] = None) -> None:
        if self._channel is None:
            if self._connection is None:
                raise ValueError("RabbitBroker not connected yet")

            max_consumers = max_consumers or self._max_consumers
            self._channel = await self._connection.channel()
            if max_consumers and self.logger:
                self.logger.info(f"Set max consumers to {max_consumers}")
                await self._channel.set_qos(prefetch_count=int(max_consumers))

    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        retry: Union[bool, int] = False,
    ) -> Callable[[Callable[..., Any]], None]:
        queue, exchange = _validate_exchange_and_queue(queue, exchange)

        if exchange and (i := len(exchange.name)) > self.__max_exchange_len:
            self.__max_exchange_len = i

        if (i := len(queue.name)) > self.__max_queue_len:
            self.__max_queue_len = i

        parent = super()

        def wrapper(func: Callable[..., Any]) -> None:
            for handler in self.handlers:
                if handler.exchange == exchange and handler.queue == queue:
                    raise ValueError(
                        f"`{func.__name__}` uses already "
                        f"using `{queue.name}` queue to listen "
                        f"`{exchange.name if exchange else 'default'}` exchange"
                    )

            func = parent._wrap_handler(func, retry, queue=queue, exchange=exchange)
            handler = Handler(callback=func, queue=queue, exchange=exchange)
            self.handlers.append(handler)

        return wrapper

    async def start(self) -> None:
        await super().start()
        await self.init_channel()

        for handler in self.handlers:
            queue = await self._init_handler(handler)

            func = handler.callback

            if self.logger:
                self._get_log_context(None, handler.queue, handler.exchange)
                self.logger.info(f"`{func.__name__}` waiting for messages")

            await queue.consume(func)

    async def publish_message(
        self,
        message: Union[aio_pika.Message, str, Dict[str, Any]],
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        **publish_args,
    ) -> Optional[aiormq.abc.ConfirmationFrameType]:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")

        queue, exchange = _validate_exchange_and_queue(queue, exchange)

        if not isinstance(message, aio_pika.Message):
            if isinstance(message, dict):
                message = aio_pika.Message(
                    json.dumps(message).encode(), content_type="application/json"
                )
            else:
                message = aio_pika.Message(message.encode(), content_type="text/plain")

        if exchange is None:
            exchange_obj = self._channel.default_exchange
        else:
            exchange_obj = await self._init_exchange(exchange)

        return await exchange_obj.publish(
            message=message,
            routing_key=queue.name,
            **publish_args,
        )

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()

    async def _init_handler(self, handler: Handler) -> aio_pika.abc.AbstractRobustQueue:
        queue = await self._init_queue(handler.queue)
        if handler.exchange is not None:
            exchange = await self._init_exchange(handler.exchange)
            await queue.bind(exchange)
        return queue

    async def _init_queue(self, queue: RabbitQueue) -> aio_pika.abc.AbstractRobustQueue:
        if queue.declare is True:
            return await self._channel.declare_queue(**queue.dict())
        else:
            return await self._channel.get_queue(queue.name, ensure=False)

    async def _init_exchange(
        self, exchange: RabbitExchange
    ) -> aio_pika.abc.AbstractRobustExchange:
        if exchange.declare is True:
            return await self._channel.declare_exchange(**exchange.dict())
        else:
            return await self._channel.get_exchange(exchange.name, ensure=False)

    def _get_log_context(
        self,
        message: Optional[aio_pika.Message],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
        **kwrags,
    ) -> Dict[str, Any]:
        exchange_name = exchange.name if exchange else "default"
        context = {
            "exchange": exchange_name,
            "queue": queue.name,
            "message_id": message.message_id[:10] if message else "",
        }
        log_context.set(context)
        return context

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(exchange)-{self.__max_exchange_len}s | "
            f"%(queue)-{self.__max_queue_len}s | "
            f"%(message_id)-10s "
            "- %(message)s"
        )

    @staticmethod
    async def _decode_message(
        message: aio_pika.IncomingMessage,
    ) -> Union[str, Dict[str, Any]]:
        body = message.body.decode()
        if message.content_type == "application/json":
            body = json.loads(body)
        return body

    @staticmethod
    def _process_message(
        func: Callable[..., Any], watcher: Optional[BaseWatcher] = None
    ) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(message: aio_pika.Message):
            if watcher is None:
                context = message.process()
            else:
                context = WatcherContext(
                    watcher,
                    message.message_id,
                    on_success=partial(message.ack),
                    on_error=partial(message.reject, True),
                    on_max=partial(message.reject, False),
                )
            async with context:
                return await func(message)

        return wrapper


def _validate_exchange_and_queue(
    queue: Union[str, RabbitQueue], exchange: Union[str, RabbitExchange, None] = None
) -> tuple[RabbitQueue, Optional[RabbitExchange]]:
    if isinstance(queue, str):
        queue = RabbitQueue(name=queue)
    elif not isinstance(queue, RabbitQueue):
        raise ValueError(f"Queue '{queue}' should be 'str' | 'RabbitQueue' instance")

    if exchange is not None:
        if isinstance(exchange, str):
            exchange = RabbitExchange(name=exchange)
        elif not isinstance(exchange, RabbitExchange):
            raise ValueError(
                f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance"
            )

    return queue, exchange
