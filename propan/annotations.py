import logging

from typing_extensions import Annotated

from propan.cli.app import PropanApp
from propan.utils.context import Context as ContextField
from propan.utils.context import ContextRepo as CR

Logger = Annotated[logging.Logger, ContextField("logger")]
App = Annotated[PropanApp, ContextField("app")]
ContextRepo = Annotated[CR, ContextField("context")]


try:
    import aio_pika

    from propan.brokers.rabbit import RabbitBroker as RB

    RabbitBroker = Annotated[RB, ContextField("broker")]
    RabbitMessage = Annotated[aio_pika.message.IncomingMessage, ContextField("message")]
except Exception:
    RabbitBroker = RabbitMessage = None  # type: ignore

try:
    from nats.aio.msg import Msg

    from propan.brokers.nats import NatsBroker as NB

    NatsBroker = Annotated[NB, ContextField("broker")]
    NatsMessage = Annotated[Msg, ContextField("message")]
except Exception:
    NatsBroker = NatsMessage = None  # type: ignore

try:
    from propan.brokers.redis import RedisBroker as RedB

    RedisBroker = Annotated[RedB, ContextField("broker")]
except Exception:
    RedisBroker = None  # type: ignore

assert any(
    (
        all((RabbitBroker, RabbitMessage)),
        all((NatsBroker, NatsMessage)),
        RedisBroker,
    )
), (
    "You should specify using broker!\n"
    "Install it using one of the following commands:\n"
    'pip install "propan[async-rabbit]"\n'
    'pip install "propan[async-nats]"\n'
    'pip install "propan[async-redis]"\n'
)
