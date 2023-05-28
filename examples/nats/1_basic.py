from propan import NatsBroker, PropanApp

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)


@broker.handle("test")
async def hello(msg: str):
    print(msg)


@app.after_startup
async def pub():
    await broker.publish("hi", "test")
