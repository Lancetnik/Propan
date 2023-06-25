from typing import Awaitable, Callable, Sequence, Union

import aio_pika
from aio_pika.message import IncomingMessage
from fast_depends.dependencies import Depends
from typing_extensions import ParamSpec, TypeAlias

from propan.brokers._model.broker_usecase import CustomDecoder, CustomParser
from propan.brokers._model.routing import BrokerRouter
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.rabbit.schemas import RabbitExchange, RabbitQueue
from propan.types import SendableMessage

P = ParamSpec("P")

PikaSendableMessage: TypeAlias = Union[aio_pika.message.Message, SendableMessage]
RabbitMessage: TypeAlias = PropanMessage[IncomingMessage]

class RabbitRouter(BrokerRouter):
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[IncomingMessage] = None,
        parse_message: CustomParser[IncomingMessage] = None,
        # AsyncAPI
        description: str = "",
    ) -> Callable[
        [
            Union[
                Callable[P, PikaSendableMessage],
                Callable[P, Awaitable[PikaSendableMessage]],
            ]
        ],
        Callable[P, PikaSendableMessage],
    ]: ...
