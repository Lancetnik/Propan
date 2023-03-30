'''
You can set specific queue and exchange to listening
with all amqp supported flags
'''
from propan.app import PropanApp
from propan.brokers import (
    RabbitExchange, ExchangeType, RabbitQueue, RabbitBroker
)


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle(queue=RabbitQueue("test"),
               exchange=RabbitExchange("test", type=ExchangeType.FANOUT))
async def base_handler(body: dict):
    print(body)
