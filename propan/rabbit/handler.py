from typing import Awaitable, Callable, Optional, Sequence

import aio_pika
from fast_depends.core import CallModel

from propan._compat import override
from propan.broker.handler import AsyncHandler
from propan.broker.message import PropanMessage
from propan.broker.middlewares import BaseMiddleware
from propan.broker.parsers import resolve_custom_func
from propan.broker.types import (
    AsyncCustomDecoder,
    AsyncCustomParser,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.rabbit.helpers import RabbitDeclarer
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
        title: Optional[str] = None,
    ):
        super().__init__(
            description=description,
            title=title,
        )

        self.queue = queue
        self.exchange = exchange
        self.consume_args = consume_args or {}

        self._consumer_tag = None
        self._queue_obj = None

    @override
    def add_call(  # type: ignore[override]
        self,
        *,
        handler: HandlerCallWrapper[
            aio_pika.IncomingMessage, P_HandlerParams, T_HandlerReturn
        ],
        dependant: CallModel[P_HandlerParams, T_HandlerReturn],
        parser: Optional[AsyncCustomParser[aio_pika.IncomingMessage]],
        decoder: Optional[AsyncCustomDecoder[aio_pika.IncomingMessage]],
        filter: Callable[[PropanMessage[aio_pika.IncomingMessage]], Awaitable[bool]],
        middlewares: Optional[
            Sequence[Callable[[aio_pika.IncomingMessage], BaseMiddleware]]
        ],
    ) -> None:
        super().add_call(
            handler=handler,
            parser=resolve_custom_func(parser, AioPikaParser.parse_message),
            decoder=resolve_custom_func(decoder, AioPikaParser.decode_message),
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
            # NOTE: aio-pika expects AbstractIncomingMessage, not IncomingMessage
            self.consume,  # type: ignore[arg-type]
            arguments=self.consume_args,
        )

    async def close(self) -> None:
        if self._queue_obj is not None:
            if self._consumer_tag is not None:  # pragma: no branch
                await self._queue_obj.cancel(self._consumer_tag)
                self._consumer_tag = None
            self._queue_obj = None
