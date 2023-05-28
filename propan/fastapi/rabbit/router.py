from propan import RabbitBroker
from propan.fastapi.core.router import PropanRouter


class RabbitRouter(PropanRouter):
    broker_class = RabbitBroker
    broker: RabbitBroker
