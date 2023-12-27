from contextlib import asynccontextmanager
from functools import wraps
from types import TracebackType
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
import anyio
from aio_pika.abc import DeliveryMode
from anyio.streams.memory import MemoryObjectReceiveStream
from fast_depends.dependencies import Depends
from typing_extensions import TypeAlias
from yarl import URL

from propan._compat import model_to_dict
from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import WRONG_PUBLISH_ARGS
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.brokers.rabbit.logging import RabbitLoggingMixin
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.brokers.rabbit.utils import validate_exchange, validate_queue
from propan.types import AnyDict, SendableMessage
from propan.utils import context

TimeoutType = Optional[Union[int, float]]
PikaSendableMessage: TypeAlias = Union[aio_pika.message.Message, SendableMessage]
RabbitMessage: TypeAlias = PropanMessage[aio_pika.message.IncomingMessage]
T = TypeVar("T")

RABBIT_REPLY = "amq.rabbitmq.reply-to"


class RabbitBroker(
    RabbitLoggingMixin,
    BrokerAsyncUsecase[aio_pika.message.IncomingMessage, aio_pika.RobustConnection],
):
    handlers: List[Handler]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]
    _queues: Dict[RabbitQueue, aio_pika.RobustQueue]
    _exchanges: Dict[RabbitExchange, aio_pika.RobustExchange]
    _rpc_lock: anyio.Lock

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
        self._rpc_lock = anyio.Lock()

        self._max_queue_len = 4
        self._max_exchange_len = 4
        self._queues = {}
        self._exchanges = {}

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)
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
        connection = await aio_pika.connect_robust(**kwargs)

        if self._channel is None:  # pragma: no branch
            max_consumers = self._max_consumers
            self._channel = await connection.channel()

            if max_consumers:
                c = self._get_log_context(None, RabbitQueue(""), RabbitExchange(""))
                self._log(f"Set max consumers to {max_consumers}", extra=c)
                await self._channel.set_qos(prefetch_count=int(max_consumers))

        return connection

    def handle(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        consume_arguments: Optional[AnyDict] = None,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[aio_pika.message.IncomingMessage, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle()

        queue, exchange = validate_queue(queue), validate_exchange(exchange)

        self._setup_log_context(queue, exchange)

        def wrapper(
            func: HandlerCallable[T_HandlerReturn],
        ) -> Callable[
            [aio_pika.message.IncomingMessage, bool], Awaitable[T_HandlerReturn]
        ]:
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
                consume_arguments=consume_arguments,
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

            await queue.consume(func, arguments=handler.consume_arguments)

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

        queue, exchange = validate_queue(queue), validate_exchange(exchange)

        if callback is True:
            if reply_to is not None:
                raise WRONG_PUBLISH_ARGS
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
                if raise_timeout:
                    scope = anyio.fail_after
                else:
                    scope = anyio.move_on_after

                msg: Any = None
                with scope(callback_timeout):
                    msg = await response_queue.receive()

                if msg:
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
            q = await self._channel.declare_queue(
                **model_to_dict(queue, exclude={"routing_key", "bind_arguments"})
            )
            self._queues[queue] = q
        return q

    async def declare_exchange(
        self, exchange: RabbitExchange
    ) -> aio_pika.RobustExchange:
        exch = self._exchanges.get(exchange)

        if exch is None:
            exch = await self._channel.declare_exchange(
                **model_to_dict(
                    exchange, exclude={"routing_key", "bind_arguments", "bind_to"}
                )
            )
            self._exchanges[exchange] = exch

        if exchange.bind_to is not None:
            parent = await self.declare_exchange(exchange.bind_to)
            await exch.bind(
                exchange=parent,
                routing_key=exchange.routing_key,
                arguments=exchange.bind_arguments,
            )

        return exch

    @staticmethod
    async def _parse_message(
        message: aio_pika.message.IncomingMessage,
    ) -> RabbitMessage:
        return PropanMessage(
            body=message.body,
            headers=message.headers,
            reply_to=message.reply_to or "",
            message_id=message.message_id or str(uuid4()),
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
                    message,
                    on_success=ack,
                    on_error=nack,
                    on_max=reject,
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

    @property
    def channel(self) -> aio_pika.RobustChannel:
        return self._channel


class RPCCallback:
    def __init__(self, lock: anyio.Lock, broker: RabbitBroker):
        self.lock = lock
        self.broker = broker

    async def __aenter__(self) -> Tuple[str, MemoryObjectReceiveStream]:
        (
            send_response_stream,
            receive_response_stream,
        ) = anyio.create_memory_object_stream(max_buffer_size=1)
        await self.lock.acquire()

        self.queue = callback_queue = await self.broker._channel.get_queue(RABBIT_REPLY)

        async def handle_response(msg: RabbitMessage) -> None:
            propan_message = await self.broker._parse_message(msg)
            await send_response_stream.send(propan_message)

        self.consumer_tag = await callback_queue.consume(handle_response, no_ack=True)

        return callback_queue.name, receive_response_stream

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ):
        self.lock.release()
        await self.queue.cancel(self.consumer_tag)


@asynccontextmanager
async def fake_context(reply_to: str) -> Tuple[str, None]:
    yield reply_to, None


async def ack(message: RabbitMessage) -> None:
    pika_message = message.raw_message
    if (
        pika_message._IncomingMessage__processed
        or pika_message._IncomingMessage__no_ack
    ):
        return
    await pika_message.ack()


async def nack(message: RabbitMessage) -> None:
    pika_message = message.raw_message
    if (
        pika_message._IncomingMessage__processed
        or pika_message._IncomingMessage__no_ack
    ):
        return
    await pika_message.nack()


async def reject(message: RabbitMessage) -> None:
    pika_message = message.raw_message
    if (
        pika_message._IncomingMessage__processed
        or pika_message._IncomingMessage__no_ack
    ):
        return
    await pika_message.reject()
