from typing import AsyncContextManager, Awaitable, Callable, List, Optional

import aio_pika
from fast_depends.core import CallModel
from typing_extensions import override

from propan.broker.handler import AsyncHandler
from propan.broker.types import (
    AsyncCustomDecoder,
    AsyncCustomParser,
    AsyncWrappedHandlerCall,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.rabbit.helpers import RabbitDeclarer
from propan.rabbit.message import RabbitMessage
from propan.rabbit.parser import AioPikaParser
from propan.rabbit.shared.schemas import BaseRMQInformation, RabbitExchange, RabbitQueue
from propan.types import AnyDict


class LogicHandler(AsyncHandler[aio_pika.IncomingMessage], BaseRMQInformation):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange]
    consume_args: AnyDict

    _consumer_tag: Optional[str]
    _queue_obj: Optional[aio_pika.RobustQueue]

    def __init__(
        self,
        queue: RabbitQueue,
        # RMQ information
        exchange: Optional[RabbitExchange] = None,
        consume_args: Optional[AnyDict] = None,
        # AsyncAPI information
        description: Optional[str] = None,
    ):
        super().__init__(
            description=description,
        )

        self.queue = queue
        self.exchange = exchange
        self.consume_args = consume_args or {}

        self._consumer_tag = None
        self._queue_obj = None

    def add_call(
        self,
        *,
        handler: HandlerCallWrapper[
            aio_pika.IncomingMessage, P_HandlerParams, T_HandlerReturn
        ],
        wrapped_call: AsyncWrappedHandlerCall[
            aio_pika.IncomingMessage, T_HandlerReturn
        ],
        dependant: CallModel[P_HandlerParams, T_HandlerReturn],
        filter: Callable[[RabbitMessage], Awaitable[bool]],
        parser: Optional[AsyncCustomParser[aio_pika.IncomingMessage]],
        decoder: Optional[AsyncCustomDecoder[aio_pika.IncomingMessage]],
        middlewares: Optional[
            List[
                Callable[
                    [RabbitMessage],
                    AsyncContextManager[None],
                ]
            ]
        ],
    ) -> None:
        super().add_call(
            handler=handler,
            wrapped_call=wrapped_call,
            parser=self._resolve_custom_func(parser, AioPikaParser.parse_message),
            decoder=self._resolve_custom_func(decoder, AioPikaParser.decode_message),
            filter=filter,
            dependant=dependant,
            middlewares=middlewares,
        )

    @override
    async def start(self, declarer: RabbitDeclarer) -> None:  # type: ignore[override]
        self._queue_obj = queue = await declarer.declare_queue(self.queue)

        if self.exchange is not None:
            exchange = await declarer.declare_exchange(self.exchange)
            await queue.bind(
                exchange,
                routing_key=self.queue.routing,
                arguments=self.queue.bind_arguments,
            )

        self._consumer_tag = await queue.consume(
            self.consume,
            arguments=self.consume_args,
        )

    async def close(self) -> None:
        if self._queue_obj is not None:
            await self._queue_obj.cancel(self._consumer_tag)
            self._queue_obj = None
