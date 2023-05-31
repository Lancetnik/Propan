from propan import NatsBroker
from propan.fastapi.core.router import PropanRouter


class NatsRouter(PropanRouter[NatsBroker]):
    broker_class = NatsBroker
