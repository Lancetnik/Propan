import asyncio
import warnings
from contextlib import asynccontextmanager
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from uuid import uuid4

import aio_pika
import aiormq
from aio_pika.abc import DeliveryMode
from fast_depends.dependencies import Depends
from typing_extensions import TypeAlias
from yarl import URL

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.types import AnyDict, DecoratedCallable, HandlerWrapper, SendableMessage
from propan.utils import context

TimeoutType = Optional[Union[int, float]]
PikaSendableMessage: TypeAlias = Union[aio_pika.message.Message, SendableMessage]
RabbitMessage: TypeAlias = PropanMessage[aio_pika.message.IncomingMessage]
T = TypeVar("T")

RABBIT_REPLY = "amq.rabbitmq.reply-to"


class RabbitBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]
    _queues: Dict[RabbitQueue, aio_pika.RobustQueue]
    _exchanges: Dict[RabbitExchange, aio_pika.RobustExchange]

    __max_queue_len: int
    __max_exchange_len: int
    _rpc_lock: asyncio.Lock

    def __init__(
        self,
        url: Union[str, URL, None] = None,
        *,
        log_fmt: Optional[str] = None,
        consumers: Optional[int] = None,
        protocol: str = "amqp",
        protocol_version: str = "0.9.1",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            url,
            log_fmt=log_fmt,
            url_=url or "amqp://guest:guest@localhost:5672/",
            protocol=protocol,
            protocol_version=protocol_version,
            **kwargs,
        )
        self._max_consumers = consumers

        self._channel = None
        self._rpc_lock = asyncio.Lock()

        self.__max_queue_len = 4
        self.__max_exchange_len = 4
        self._queues = {}
        self._exchanges = {}

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

        self._queues = {}
        self._exchanges = {}

    async def _connect(
        self,
        **kwargs: Any,
    ) -> aio_pika.RobustConnection:
        connection = await aio_pika.connect_robust(
            **kwargs, loop=asyncio.get_event_loop()
        )

        if self._channel is None:  # pragma: no branch
            max_consumers = self._max_consumers
            self._channel = await connection.channel()

            if max_consumers:
                c = self._get_log_context(None, RabbitQueue(""), RabbitExchange(""))
                self._log(f"Set max consumers to {max_consumers}", extra=c)
                await self._channel.set_qos(prefetch_count=int(self._max_consumers))

        return connection

    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> HandlerWrapper:
        super().handle()

        queue, exchange = _validate_queue(queue), _validate_exchange(exchange)

        self.__setup_log_context(queue, exchange)

        def wrapper(func: DecoratedCallable) -> Any:
            func, dependant = self._wrap_handler(
                func,
                queue=queue,
                exchange=exchange,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                queue=queue,
                exchange=exchange,
                _description=description,
                dependant=dependant,
            )
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, RabbitQueue(""), RabbitExchange("")),
        )

        await super().start()

        for handler in self.handlers:
            queue = await self._init_handler(handler)

            func = handler.callback

            c = self._get_log_context(None, handler.queue, handler.exchange)
            self._log(f"`{func.__name__}` waiting for messages", extra=c)

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
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs,
    ) -> Union[aiormq.abc.ConfirmationFrameType, Dict, str, bytes, None]:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")

        queue, exchange = _validate_queue(queue), _validate_exchange(exchange)

        if callback is True:
            if reply_to is not None:
                raise ValueError(
                    "You should use `reply_to` to send response to long-living queue "
                    "and `callback` to get response in sync mode."
                )
            else:
                context = RPCCallback(self._rpc_lock, self)
        else:
            context = fake_context(reply_to)

        if exchange is None:
            exchange_obj = self._channel.default_exchange
        else:
            exchange_obj = await self.declare_exchange(exchange)

        async with context as (reply_to, response_queue):
            message = self._validate_message(
                message=message,
                persist=persist,
                reply_to=reply_to,
                **message_kwargs,
            )

            r = await exchange_obj.publish(
                message=message,
                routing_key=routing_key or queue.routing or "",
                mandatory=mandatory,
                immediate=immediate,
                timeout=timeout,
            )

            if response_queue is None:
                return r

            else:
                try:
                    msg = await asyncio.wait_for(response_queue.get(), callback_timeout)
                except asyncio.TimeoutError as e:
                    if raise_timeout is True:  # pragma: no branch
                        raise e
                else:
                    return await self._decode_message(msg)

    async def _init_handler(
        self,
        handler: Handler,
    ) -> aio_pika.abc.AbstractRobustQueue:
        queue = await self.declare_queue(handler.queue)
        if handler.exchange is not None and handler.exchange.name != "default":
            exchange = await self.declare_exchange(handler.exchange)
            await queue.bind(
                exchange,
                routing_key=handler.queue.routing,
                arguments=handler.queue.bind_arguments,
            )
        return queue

    async def declare_queue(self, queue: RabbitQueue) -> aio_pika.RobustQueue:
        q = self._queues.get(queue)
        if q is None:
            q = await self._channel.declare_queue(**queue.dict())
            self._queues[queue] = q
        return q

    async def declare_exchange(
        self, exchange: RabbitExchange
    ) -> aio_pika.RobustExchange:
        exch = self._exchanges.get(exchange)

        if exch is None:
            exch = await self._channel.declare_exchange(**exchange.dict())
            self._exchanges[exchange] = exch

            current = exchange
            current_exch = exch
            while current.bind_to is not None:
                parent_exch = await self._channel.declare_exchange(
                    **current.bind_to.dict()
                )
                await current_exch.bind(
                    exchange=parent_exch,
                    routing_key=current.routing_key,
                    arguments=current.bind_arguments,
                )
                current = current.bind_to
                current_exch = parent_exch

        return exch

    def _get_log_context(
        self,
        message: Optional[RabbitMessage],
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
    ) -> RabbitMessage:
        return RabbitMessage(
            body=message.body,
            headers=message.headers,
            reply_to=message.reply_to or "",
            message_id=message.message_id,
            content_type=message.content_type or "",
            raw_message=message,
        )

    def _process_message(
        self,
        func: Callable[[RabbitMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[RabbitMessage], Awaitable[T]]:
        @wraps(func)
        async def wrapper(message: RabbitMessage) -> T:
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
                if message.reply_to:
                    await self.publish(
                        message=r,
                        routing_key=message.reply_to,
                        correlation_id=pika_message.correlation_id,
                    )

                return r

        return wrapper

    @classmethod
    def _validate_message(
        cls: Type["RabbitBroker"],
        message: PikaSendableMessage,
        persist: bool = False,
        callback_queue: Optional[aio_pika.abc.AbstractRobustQueue] = None,
        reply_to: Optional[str] = None,
        **message_kwargs: Dict[str, Any],
    ) -> aio_pika.Message:
        if not isinstance(message, aio_pika.message.Message):
            message, content_type = super()._encode_message(message)

            delivery_mode = (
                DeliveryMode.PERSISTENT if persist else DeliveryMode.NOT_PERSISTENT
            )

            message = aio_pika.Message(
                message,
                **{
                    "delivery_mode": delivery_mode,
                    "content_type": content_type,
                    "reply_to": callback_queue or reply_to,
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
            self.__max_exchange_len = max(self.__max_exchange_len, len(exchange.name))

        if queue is not None:  # pragma: no branch
            self.__max_queue_len = max(self.__max_queue_len, len(queue.name))

    @property
    def channel(self) -> aio_pika.RobustChannel:
        return self._channel

    async def _init_queue(
        self,
        queue: RabbitQueue,
    ) -> aio_pika.abc.AbstractRobustQueue:
        # TODO: remove method
        warnings.warn(
            "The `_init_queue` method is deprecated, "  # noqa: E501
            "and will be removed in version 1.4.0. "  # noqa: E501
            "Use `declare_queue` instead.",  # noqa: E501
            category=DeprecationWarning,
            stacklevel=1,
        )

        q = self._queues.get(queue)
        if q is None:  # pragma: no cover
            q = await self._channel.declare_queue(**queue.dict())
            self._queues[queue] = q
        return q

    async def _init_exchange(
        self,
        exchange: RabbitExchange,
    ) -> aio_pika.abc.AbstractRobustExchange:
        # TODO: remove method
        warnings.warn(
            "The `_init_exchange` method is deprecated, "  # noqa: E501
            "and will be removed in version 1.4.0. "  # noqa: E501
            "Use `declare_exchange` instead.",  # noqa: E501
            category=DeprecationWarning,
            stacklevel=1,
        )

        exch = self._exchanges.get(exchange)

        if exch is None:  # pragma: no cover
            exch = await self._channel.declare_exchange(**exchange.dict())
            self._exchanges[exchange] = exch

            current = exchange
            current_exch = exch
            while current.bind_to is not None:
                parent_exch = await self._channel.declare_exchange(
                    **current.bind_to.dict()
                )
                await current_exch.bind(
                    exchange=parent_exch,
                    routing_key=current.routing_key,
                    arguments=current.bind_arguments,
                )
                current = current.bind_to
                current_exch = parent_exch

        return exch


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


class RPCCallback:
    def __init__(self, lock: asyncio.Lock, broker: RabbitBroker):
        self.lock = lock
        self.broker = broker

    async def __aenter__(self) -> Tuple[str, asyncio.Queue]:
        response_queue: asyncio.Queue[PropanMessage] = asyncio.Queue(1)
        await self.lock.acquire()

        self.queue = callback_queue = await self.broker._channel.get_queue(RABBIT_REPLY)

        async def handle_response(msg: RabbitMessage) -> None:
            propan_message = await self.broker._parse_message(msg)
            await response_queue.put(propan_message)

        self.consumer_tag = await callback_queue.consume(handle_response, no_ack=True)

        return callback_queue.name, response_queue

    async def __aexit__(self, *args, **kwargs):
        self.lock.release()
        await self.queue.cancel(self.consumer_tag)


@asynccontextmanager
async def fake_context(reply_to: str) -> Tuple[str, None]:
    yield reply_to, None
