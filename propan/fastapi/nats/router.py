from nats.aio.msg import Msg

from propan.brokers.nats import NatsBroker, NatsJSBroker
from propan.fastapi.core.router import PropanRouter


class NatsRouter(PropanRouter[NatsBroker, Msg]):
    broker_class = NatsBroker


class NatsJSRouter(PropanRouter[NatsJSBroker, Msg]):
    broker_class = NatsJSBroker
