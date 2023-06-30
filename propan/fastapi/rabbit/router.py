from aio_pika.message import IncomingMessage

from propan import RabbitBroker
from propan.fastapi.core.router import PropanRouter


class RabbitRouter(PropanRouter[RabbitBroker, IncomingMessage]):
    broker_class = RabbitBroker
