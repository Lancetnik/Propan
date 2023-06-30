from aio_pika.message import IncomingMessage

from propan.brokers._model.routing import BrokerRouter


class RabbitRouter(BrokerRouter[IncomingMessage]):
    pass
