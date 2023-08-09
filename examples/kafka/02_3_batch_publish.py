from propan import Logger, PropanApp
from propan.kafka import KafkaBroker

broker = KafkaBroker("localhost:9092")
app = PropanApp(broker)


@broker.subscriber("test")
@broker.publisher("response", batch=True)
async def handler():
    return ("hi", "propan")


@broker.subscriber("response", batch=True)
async def response_handler(msg: list[str], logger: Logger):
    logger.info(msg)


@app.after_startup
async def test() -> None:
    await broker.publish("hi", "test")
