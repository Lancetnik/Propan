from propan import PropanApp, NatsBroker

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)

@broker.handle("test")
async def handle(m: str):
    await broker.publish(m, "another-queue")