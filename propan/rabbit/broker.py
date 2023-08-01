import logging
from functools import wraps
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

import aio_pika
import aiormq
from fast_depends.dependencies import Depends
from yarl import URL

from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.push_back_watcher import BaseWatcher, OneTryWatcher, WatcherContext
from propan.broker.types import (
    AsyncDecoder,
    AsyncParser,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.exceptions import RuntimeException
from propan.rabbit.asyncapi import Handler
from propan.rabbit.helpers import AioPikaPublisher, RabbitDeclarer
from propan.rabbit.message import RabbitMessage
from propan.rabbit.publisher import Publisher
from propan.rabbit.shared.constants import RABBIT_REPLY
from propan.rabbit.shared.logging import RabbitLoggingMixin
from propan.rabbit.shared.publisher import AMQPHandlerCallWrapper
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue, get_routing_hash
from propan.rabbit.shared.types import TimeoutType
from propan.rabbit.types import AioPikaSendableMessage
from propan.types import AnyDict, DecodedMessage
from propan.utils import context
from propan.utils.functions import to_async


class RabbitBroker(
    RabbitLoggingMixin,
    BrokerAsyncUsecase[aio_pika.IncomingMessage, aio_pika.RobustConnection],
):
    handlers: Dict[int, Handler]
    declarer: Optional[RabbitDeclarer]
    _publisher: Optional[AioPikaPublisher]
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]

    _publishers: List[Publisher]

    def __init__(
        self,
        url: Union[str, URL, None] = "amqp://guest:guest@localhost:5672/",
        *,
        max_consumers: Optional[int] = None,
        protocol: str = "amqp",
        protocol_version: Optional[str] = "0.9.1",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            url=url,
            protocol=protocol,
            protocol_version=protocol_version,
            **kwargs,
        )

        self._max_consumers = max_consumers

        self._channel = None
        self.declarer = None
        self._publisher = None

    async def _close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None

        if self.declarer is not None:
            self.declarer = None

        if self._publisher is not None:
            self._publisher = None

        await self._connection.close()
        await super()._close(exc_type, exc_val, exec_tb)

    async def connect(self, *args: Any, **kwargs: AnyDict) -> aio_pika.RobustConnection:
        connection = await super().connect(*args, **kwargs)
        for p in self._publishers:
            p._publisher = self._publisher
        return connection

    async def _connect(
        self,
        **kwargs: Any,
    ) -> aio_pika.RobustConnection:
        connection = await aio_pika.connect_robust(**kwargs)

        if self._channel is None:  # pragma: no branch
            max_consumers = self._max_consumers
            channel = self._channel = await connection.channel()

            declarer = self.declarer = RabbitDeclarer(channel)
            self.declarer.queues[RABBIT_REPLY] = await channel.get_queue(
                RABBIT_REPLY,
                ensure=False,
            )

            self._publisher = AioPikaPublisher(
                channel,
                declarer,
                global_decoder=self._global_decoder,
                global_parser=self._global_parser,
            )

            if max_consumers:
                c = self._get_log_context(None, RabbitQueue(""), RabbitExchange(""))
                self._log(f"Set max consumers to {max_consumers}", extra=c)
                await channel.set_qos(prefetch_count=int(max_consumers))

        return connection

    async def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, RabbitQueue(""), RabbitExchange("")),
        )

        await super().start()
        assert self.declarer, "Declarer should be initialized in `connect` method"

        for handler in self.handlers.values():
            c = self._get_log_context(None, handler.queue, handler.exchange)
            self._log(f"`{handler.name}` waiting for messages", extra=c)
            await handler.start(self.declarer)

    def subscriber(
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        consume_args: Optional[AnyDict] = None,
        # broker arguments
        dependencies: Sequence[Depends] = (),
        parser: Optional[AsyncParser[aio_pika.IncomingMessage]] = None,
        decoder: Optional[AsyncDecoder[aio_pika.IncomingMessage]] = None,
        middlewares: Optional[
            List[
                Callable[
                    [RabbitMessage],
                    AsyncContextManager[None],
                ]
            ]
        ] = None,
        filter: Callable[
            [RabbitMessage],
            Union[bool, Awaitable[bool]],
        ] = lambda m: not m.processed,
        # AsyncAPI information
        description: Optional[str] = None,
        **original_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        AMQPHandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        super().subscriber()

        r_queue = RabbitQueue.validate(queue)
        r_exchange = RabbitExchange.validate(exchange)

        self._setup_log_context(r_queue, r_exchange)

        key = get_routing_hash(r_queue, r_exchange)
        handler = self.handlers.get(
            key,
            Handler(
                queue=r_queue,
                exchange=r_exchange,
                consume_args=consume_args,
                description=description,
            ),
        )

        self.handlers[key] = handler

        def consumer_wrapper(
            func: Callable[P_HandlerParams, T_HandlerReturn],
        ) -> AMQPHandlerCallWrapper[P_HandlerParams, T_HandlerReturn]:
            handler_call: AMQPHandlerCallWrapper
            wrapped_func, handler_call, dependant = self._wrap_handler(
                func,
                extra_dependencies=dependencies,
                **original_kwargs,
                queue=r_queue,
                exchange=r_exchange,
            )

            handler.add_call(
                handler=handler_call,
                wrapped_call=wrapped_func,
                filter=to_async(filter),
                middlewares=middlewares,
                parser=parser or self._global_parser,
                decoder=decoder or self._global_decoder,
                dependant=dependant,
            )

            return handler_call

        return consumer_wrapper

    def publisher(
        self,
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Publisher:
        publisher = Publisher(
            queue=RabbitQueue.validate(queue),
            exchange=RabbitExchange.validate(exchange),
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
            persist=persist,
            reply_to=reply_to,
            message_kwargs=message_kwargs,
            _publisher=self._publisher,
        )
        return super().publisher(publisher)

    async def publish(
        self,
        message: AioPikaSendableMessage = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Union[aiormq.abc.ConfirmationFrameType, DecodedMessage, None]:
        if self._channel is None:
            raise ValueError("RabbitBroker channel not started yet")
        return await self._publisher.publish(
            message=message,
            queue=queue,
            exchange=exchange,
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
            rpc=rpc,
            rpc_timeout=rpc_timeout,
            raise_timeout=raise_timeout,
            persist=persist,
            reply_to=reply_to,
            **message_kwargs,
        )

    def _process_message(
        self,
        func: Callable[[RabbitMessage], Awaitable[T_HandlerReturn]],
        call_wrapper: AMQPHandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[RabbitMessage], Awaitable[T_HandlerReturn]]:
        if watcher is None:
            watcher = OneTryWatcher()

        @wraps(func)
        async def process_wrapper(message: RabbitMessage) -> T_HandlerReturn:
            async with WatcherContext(watcher, message):
                try:
                    r = await self._execute_handler(func, message)

                except RuntimeException:
                    pass

                else:
                    if message.reply_to:
                        await self.publish(
                            message=r,
                            routing_key=message.reply_to,
                            correlation_id=message.correlation_id,
                        )

                    for publisher in call_wrapper._publishers:
                        try:
                            await publisher.publish(
                                message=r,
                                correlation_id=message.correlation_id,
                            )
                        except Exception as e:
                            self._log(
                                f"Publish exception: {e}",
                                logging.ERROR,
                                self._get_log_context(
                                    context.get_local("message"),
                                    getattr(publisher, "queue", RabbitQueue("")),
                                    getattr(publisher, "exchange", None),
                                ),
                            )

                    return r

        return process_wrapper

    @property
    def channel(self) -> aio_pika.RobustChannel:
        return self._channel

    async def declare_queue(
        self,
        queue: RabbitQueue,
    ) -> aio_pika.RobustQueue:
        assert self.declarer, "Declarer should be initialized in `connect` method"
        return await self.declarer.declare_queue(queue)

    async def declare_exchange(
        self,
        exchange: RabbitExchange,
    ) -> aio_pika.RobustExchange:
        assert self.declarer, "Declarer should be initialized in `connect` method"
        return await self.declarer.declare_exchange(exchange)
