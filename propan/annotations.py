import logging

from propan.cli.app import PropanApp
from propan.utils.context import Context as ContextField
from propan.utils.context import ContextRepo as CR
from typing_extensions import Annotated

Logger = Annotated[logging.Logger, ContextField("logger")]
App = Annotated[PropanApp, ContextField("app")]
ContextRepo = Annotated[CR, ContextField("context")]

RabbitBroker = NatsBroker = RabbitMessage = NatsMessage = None

try:
    import aio_pika
    from propan.brokers.rabbit import RabbitBroker as RB

    RabbitBroker = Annotated[RB, ContextField("broker")]
    RabbitMessage = Annotated[aio_pika.IncomingMessage, ContextField("message")]
except Exception:
    pass

try:
    from nats.aio.msg import Msg
    from propan.brokers.nats import NatsBroker as NB

    NatsBroker = Annotated[NB, ContextField("broker")]
    NatsMessage = Annotated[Msg, ContextField("message")]
except Exception:
    pass

assert any(
    (
        all((RabbitBroker, RabbitMessage)),
        all((NatsBroker, NatsMessage)),
    )
), "You should specify using broker!"
