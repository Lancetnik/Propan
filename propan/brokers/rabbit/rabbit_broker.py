import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union
from uuid import uuid4

import aio_pika
import aiormq

from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.types import AnyDict, DecoratedCallable, SendableMessage, Wrapper
from propan.utils.context import context as global_context

TimeoutType = Optional[Union[int, float]]
PikaSendableMessage = Union[aio_pika.message.Message, SendableMessage]
T = TypeVar("T")


class RabbitBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]

    __max_queue_len: int
    __max_exchange_len: int

    def __init__(
        self,
        *args: Tuple[Any, ...],
        consumers: Optional[int] = None,
        log_fmt: Optional[str] = None,
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(*args, log_fmt=log_fmt, **kwargs)
        self._max_consumers = consumers

        self._channel = None
        self.handlers = []

        self.__max_queue_len = 4
        self.__max_exchange_len = 4

    async def __aenter__(self) -> "RabbitBroker":
        await self.connect()
        await self._init_channel()
        return self

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()

    async def _connect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> aio_pika.Connection:
        return await aio_pika.connect_robust(
            *args, **kwargs, loop=asyncio.get_event_loop()
        )

    async def _init_channel(
        self,
        max_consumers: Optional[int] = None,
    ) -> None:
        if self._channel is None:
            if self._connection is None:
                raise ValueError("RabbitBroker not connected yet")

            max_consumers = max_consumers or self._max_consumers
            self._channel = await self._connection.channel()

            if max_consumers:
                self._log(f"Set max consumers to {max_consumers}", logging.INFO)
                await self._channel.set_qos(prefetch_count=int(max_consumers))

    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        **original_kwargs,
    ) -> Wrapper:
        queue, exchange = _validate_queue(queue), _validate_exchange(exchange)

        self.__setup_log_context(queue, exchange)

        def wrapper(func: DecoratedCallable) -> Any:
            for handler in self.handlers:
                if handler.exchange == exchange and handler.queue == queue:
                    raise ValueError(
                        f"`{func.__name__}` uses already "
                        f"using `{queue.name}` queue to listen "
                        f"`{exchange.name if exchange else 'default'}` exchange"
                    )

            func = self._wrap_handler(
                func,
                queue=queue,
                exchange=exchange,
                **original_kwargs,
            )
            handler = Handler(callback=func, queue=queue, exchange=exchange)
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        await super().start()
        await self._init_channel()

        for handler in self.handlers:
            queue = await self._init_handler(handler)

            func = handler.callback

            if self.logger is not None:
                context = self._get_log_context(None, handler.queue, handler.exchange)
                global_context.set_local("log_context", context)
                self.logger.info(f"`{func.__name__}` waiting for messages")

            await queue.consume(func)

    async def publish(
        self,
        message: PikaSendableMessage = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        **message_kwargs,
    ) -> Union[aiormq.abc.ConfirmationFrameType, Dict, str, bytes, None]:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")

        queue, exchange = _validate_queue(queue), _validate_exchange(exchange)

        if callback is not False:
            callback_queue = await self._channel.declare_queue(exclusive=True)
        else:
            callback_queue = None

        if exchange is None:
            exchange_obj = self._channel.default_exchange
        else:
            exchange_obj = await self._init_exchange(exchange)

        message = self._validate_message(message, callback_queue, **message_kwargs)

        r = await exchange_obj.publish(
            message=message,
            routing_key=routing_key or queue.name,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
        )

        if callback_queue is None:
            return r

        else:
            try:
                async with callback_queue.iterator(
                    timeout=callback_timeout
                ) as queue_iterator:
                    async for m in queue_iterator:  # pragma: no branch
                        return await self._decode_message(m)
            except asyncio.TimeoutError as e:
                if raise_timeout is True:  # pragma: no branch
                    raise e

    async def _init_handler(
        self,
        handler: Handler,
    ) -> aio_pika.abc.AbstractRobustQueue:
        queue = await self._init_queue(handler.queue)
        if handler.exchange is not None and handler.exchange.name != "default":
            exchange = await self._init_exchange(handler.exchange)
            await queue.bind(exchange, handler.queue.routing_key or handler.queue.name)
        return queue

    async def _init_queue(
        self,
        queue: RabbitQueue,
    ) -> aio_pika.abc.AbstractRobustQueue:
        return await self._channel.declare_queue(**queue.dict())

    async def _init_exchange(
        self,
        exchange: RabbitExchange,
    ) -> aio_pika.abc.AbstractRobustExchange:
        return await self._channel.declare_exchange(**exchange.dict())

    def _get_log_context(
        self,
        message: Optional[PropanMessage],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
    ) -> Dict[str, Any]:
        context = {
            "queue": queue.name,
            "exchange": exchange.name if exchange else "default",
            **super()._get_log_context(message),
        }
        return context

    @property
    def fmt(self) -> str:
        return super().fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(exchange)-{self.__max_exchange_len}s | "
            f"%(queue)-{self.__max_queue_len}s | "
            f"%(message_id)-10s "
            "- %(message)s"
        )

    @staticmethod
    async def _parse_message(
        message: aio_pika.message.IncomingMessage,
    ) -> PropanMessage:
        return PropanMessage(
            body=message.body,
            headers=message.headers,
            message_id=message.message_id,
            content_type=message.content_type or "",
            raw_message=message,
        )

    def _process_message(
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            pika_message = message.raw_message
            if watcher is None:
                context = pika_message.process()
            else:
                context = WatcherContext(
                    watcher,
                    message.message_id,
                    on_success=pika_message.ack,
                    on_error=pika_message.nack,
                    on_max=pika_message.reject,
                )

            async with context:
                r = await func(message)
                if message.raw_message.reply_to:
                    await self.publish(
                        r,
                        routing_key=pika_message.reply_to,
                        correlation_id=pika_message.correlation_id,
                    )

                return r

        return wrapper

    @classmethod
    def _validate_message(
        cls: Type["RabbitBroker"],
        message: PikaSendableMessage,
        callback_queue: Optional[aio_pika.abc.AbstractRobustQueue] = None,
        **message_kwargs: Dict[str, Any],
    ) -> aio_pika.Message:
        if not isinstance(message, aio_pika.message.Message):
            message, content_type = super()._encode_message(message)

            message = aio_pika.Message(
                message,
                **{
                    "content_type": content_type,
                    "reply_to": callback_queue,
                    "correlation_id": str(uuid4()),
                    **message_kwargs,
                },
            )

        return message

    def __setup_log_context(
        self,
        queue: Optional[RabbitQueue] = None,
        exchange: Optional[RabbitExchange] = None,
    ) -> None:
        if exchange is not None:
            i = len(exchange.name)
            if i > self.__max_exchange_len:  # pragma: no branch
                self.__max_exchange_len = i

        if queue is not None:  # pragma: no branch
            i = len(queue.name)
            if i > self.__max_queue_len:  # pragma: no branch
                self.__max_queue_len = i


def _validate_exchange(
    exchange: Union[str, RabbitExchange, None] = None,
) -> Optional[RabbitExchange]:
    if exchange is not None:  # pragma: no branch
        if isinstance(exchange, str):
            exchange = RabbitExchange(name=exchange)
        elif not isinstance(exchange, RabbitExchange):
            raise ValueError(
                f"Exchange '{exchange}' should be 'str' | 'RabbitExchange' instance"
            )
    return exchange


def _validate_queue(
    queue: Union[str, RabbitQueue, None] = None
) -> Optional[RabbitQueue]:
    if queue is not None:  # pragma: no branch
        if isinstance(queue, str):
            queue = RabbitQueue(name=queue)
        elif not isinstance(queue, RabbitQueue):
            raise ValueError(
                f"Queue '{queue}' should be 'str' | 'RabbitQueue' instance"
            )
    return queue
