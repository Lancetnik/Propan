from typing import Awaitable, Callable, Optional, Sequence, Union

import aio_pika
from aio_pika.message import IncomingMessage
from fast_depends.dependencies import Depends
from typing_extensions import TypeAlias

from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.routing import BrokerRouter
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.rabbit.schemas import RabbitExchange, RabbitQueue
from propan.types import AnyDict, SendableMessage

PikaSendableMessage: TypeAlias = Union[aio_pika.message.Message, SendableMessage]
RabbitMessage: TypeAlias = PropanMessage[IncomingMessage]

class RabbitRouter(BrokerRouter[IncomingMessage]):
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        consume_arguments: Optional[AnyDict] = None,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        # AsyncAPI
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[IncomingMessage, bool], Awaitable[T_HandlerReturn]],
    ]: ...
