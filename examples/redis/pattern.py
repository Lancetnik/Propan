from propan import PropanApp, RedisBroker
from propan.annotations import Logger

broker = RedisBroker()
app = PropanApp(broker)


@broker.handle("*.info", pattern=True)
async def handler1(b: str, logger: Logger):
    logger.info("handler1")


@broker.handle("*.info", pattern=True)
async def handler2(b: str, logger: Logger):
    logger.info("handler2")


@broker.handle("*.error", pattern=True)
async def handler3(logger: Logger):
    logger.info("handler3")


@app.after_startup
async def publish_smth():
    await broker.publish("", "logs.info")
    await broker.publish("", "logs.error")
