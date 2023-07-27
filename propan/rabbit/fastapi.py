from aio_pika.message import IncomingMessage

from propan.broker.fastapi.router import PropanRouter
from propan.rabbit.broker import RabbitBroker


class RabbitRouter(PropanRouter[RabbitBroker, IncomingMessage]):
    broker_class = RabbitBroker
