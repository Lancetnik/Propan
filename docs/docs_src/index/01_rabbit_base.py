from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    print(body)