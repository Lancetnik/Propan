'''
Connect to localhost RabbitMQ and listen `default` exchange
with `test` routing key

use `propan run basic_usage:app` to start example
'''

from propan.app import PropanApp
from propan.brokers import RabbitBroker


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body: dict):
    print(body)
