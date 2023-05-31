from propan import RabbitBroker
from propan.fastapi.core.router import PropanRouter


class RabbitRouter(PropanRouter[RabbitBroker]):
    broker_class = RabbitBroker
