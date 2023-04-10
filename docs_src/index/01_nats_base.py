from propan import PropanApp
from propan.brokers.nats import NatsBroker

broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    '''Handle all default exchange messages with `test` routing key'''
    print(body)