from propan import PropanApp, SQSBroker

broker = SQSBroker("http://localhost:9324", ...)
app = PropanApp(broker)

@broker.handle("test")
async def handle(m: str):
    await broker.publish(m, "another-queue")