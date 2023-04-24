import asyncio
import json
import logging
from functools import wraps
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aio_pika
import aiormq
from propan.brokers.model import BrokerUsecase, ContentTypes
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.types import DecodedMessage, DecoratedCallable, Wrapper
from propan.utils.context.main import log_context
from propan.utils.functions import async_partial
from pydantic import BaseModel

TimeoutType = Optional[Union[int, float]]


class RabbitBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]

    __max_queue_len: int
    __max_exchange_len: int

    def __init__(
        self,
        *args: Any,
        consumers: Optional[int] = None,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ):
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

    async def _connect(self, *args: Any, **kwargs: Any) -> aio_pika.Connection:
        return await aio_pika.connect_robust(
            *args, **kwargs, loop=asyncio.get_event_loop()
        )

    async def _init_channel(self, max_consumers: Optional[int] = None) -> None:
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
        *,
        retry: Union[bool, int] = False,
    ) -> Wrapper:
        queue, exchange = _validate_queue(queue), _validate_exchange(exchange)

        if exchange:
            i = len(exchange.name)
            if i > self.__max_exchange_len:  # pragma: no branch
                self.__max_exchange_len = i

        i = len(queue.name)
        if i > self.__max_queue_len:  # pragma: no branch
            self.__max_queue_len = i

        def wrapper(func: DecoratedCallable) -> Any:
            for handler in self.handlers:
                if handler.exchange == exchange and handler.queue == queue:
                    raise ValueError(
                        f"`{func.__name__}` uses already "
                        f"using `{queue.name}` queue to listen "
                        f"`{exchange.name if exchange else 'default'}` exchange"
                    )

            func = self._wrap_handler(func, retry, queue=queue, exchange=exchange)
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
                self._get_log_context(None, handler.queue, handler.exchange)
                self.logger.info(f"`{func.__name__}` waiting for messages")

            await queue.consume(func)

    async def publish(
        self,
        message: Union[aio_pika.Message, str, Dict[str, Any], BaseModel] = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        callback: bool = False,
        callback_timeout: float | None = 30.0,
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

        message = _validate_message(message, callback_queue, **message_kwargs)

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
            async with callback_queue.iterator() as queue_iterator:
                try:
                    message = await asyncio.wait_for(
                        anext(queue_iterator), timeout=callback_timeout
                    )
                except asyncio.TimeoutError as e:
                    if raise_timeout is True:
                        raise e
                else:
                    return await self._decode_message(message)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()

    async def _init_handler(self, handler: Handler) -> aio_pika.abc.AbstractRobustQueue:
        queue = await self._init_queue(handler.queue)
        if handler.exchange is not None and handler.exchange.name != "default":
            exchange = await self._init_exchange(handler.exchange)
            await queue.bind(exchange, handler.queue.routing_key or handler.queue.name)
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
    ) -> DecodedMessage:
        body = message.body
        if message.content_type is not None:
            if ContentTypes.text.value in message.content_type:
                body = body.decode()
            elif ContentTypes.json.value in message.content_type:  # pragma: no branch
                body = json.loads(body.decode())
        return body

    def _process_message(
        self, func: DecoratedCallable, watcher: Optional[BaseWatcher] = None
    ) -> DecoratedCallable:
        @wraps(func)
        async def wrapper(message: aio_pika.IncomingMessage):
            if watcher is None:
                context = message.process()
            else:
                context = WatcherContext(
                    watcher,
                    message.message_id,
                    on_success=message.ack,
                    on_error=async_partial(message.reject, True),
                    on_max=async_partial(message.reject, False),
                )

            async with context:
                r = await func(message)
                if message.reply_to:
                    await self.publish(
                        r,
                        routing_key=message.reply_to,
                        correlation_id=message.correlation_id,
                    )

                return r

        return wrapper


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


def _validate_message(
    message: Union[aio_pika.Message, str, Dict[str, Any], BaseModel],
    callback_queue: Optional[aio_pika.abc.AbstractRobustQueue] = None,
    **message_kwargs: Dict[str, Any],
) -> aio_pika.Message:
    if not isinstance(message, aio_pika.message.Message):
        if isinstance(message, BaseModel):
            message = json.dumps(message.dict())
            content_type = ContentTypes.json.value
        elif isinstance(message, dict):
            message = json.dumps(message)
            content_type = ContentTypes.json.value
        else:
            content_type = ContentTypes.text.value

        message = aio_pika.Message(
            message.encode(),
            **{
                "content_type": content_type,
                "reply_to": callback_queue,
                "correlation_id": str(uuid4()),
                **message_kwargs,
            },
        )

    return message
