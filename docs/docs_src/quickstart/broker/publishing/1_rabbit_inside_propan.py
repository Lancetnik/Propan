from propan import PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)

@broker.handle("test")
async def handle(m: str):
    await broker.publish(m, "another-queue")