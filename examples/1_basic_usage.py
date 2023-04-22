"""
Connect to localhost RabbitMQ and listen `default` exchange
with `test` routing key

use `propan run basic_usage:app` to start example
"""
from propan import PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body):
    print(body)
