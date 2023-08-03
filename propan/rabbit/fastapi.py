from propan.broker.fastapi.router import PropanRouter
from propan.rabbit.broker import RabbitBroker


class RabbitRouter(PropanRouter[RabbitBroker]):
    broker_class = RabbitBroker
