from propan import PropanApp, RedisBroker

broker = RedisBroker("redis://localhost:6379")
app = PropanApp(broker)

@broker.handle("test")
async def handle(m: str):
    await broker.publish(m, "another-channel")