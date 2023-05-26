from propan import NatsBroker
from propan.fastapi.core.router import PropanRouter


class NatsRouter(PropanRouter):
    broker_class = NatsBroker
    broker: NatsBroker
