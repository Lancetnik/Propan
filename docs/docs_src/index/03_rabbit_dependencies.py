from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker

gl_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(gl_broker)

@gl_broker.handle("test")
async def base_handler(body: dict,
                       broker: RabbitBroker = Context()):
    assert broker is gl_broker