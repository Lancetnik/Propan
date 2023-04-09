from propan import PropanApp, Depends, use_context

from propan.brokers.rabbit import RabbitBroker

# from propan.brokers.nats import NatsBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
# broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)


async def dep(body):
    print(b)

@broker.handle("test")
async def base_handler(body, message, k = Depends(dep)):
    '''Handle all default exchange messages with `test` routing key'''
    print(body)
    print(message)
