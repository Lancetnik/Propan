from nats.aio.msg import Msg

from propan import NatsBroker
from propan.fastapi.core.router import PropanRouter


class NatsRouter(PropanRouter[NatsBroker, Msg]):
    broker_class = NatsBroker
