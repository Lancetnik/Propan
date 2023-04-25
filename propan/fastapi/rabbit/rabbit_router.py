from core.router import PropanRouter

from propan.brokers.rabbit import RabbitBroker


class RabbitRouter(PropanRouter):
    broker_class = RabbitBroker
