from propan import PropanApp, NatsBroker

broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    print(body)