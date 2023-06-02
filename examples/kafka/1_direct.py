from propan import KafkaBroker, PropanApp

broker = KafkaBroker("localhost:9092")
app = PropanApp(broker)


@broker.handle("test-topic", auto_offset_reset="earliest")
async def hello(msg: str):
    print(msg)


@app.after_startup
async def pub():
    await broker.publish("hi", "test-topic")
