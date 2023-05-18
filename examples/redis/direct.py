from propan import PropanApp, RedisBroker
from propan.annotations import Logger

broker = RedisBroker()
app = PropanApp(broker)


@broker.handle("test")
async def handler1(logger: Logger):
    logger.info("handler1")


@broker.handle("test")
async def handler2(logger: Logger):
    logger.info("handler2")


@broker.handle("test2")
async def handler3(logger: Logger):
    logger.info("handler3")


@app.after_startup
async def publish_smth():
    await broker.publish("", "test")
    await broker.publish("", "test2")
