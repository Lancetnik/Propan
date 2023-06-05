from propan import PropanApp, NatsBroker
from propan.annotations import Logger

broker = NatsBroker()
app = PropanApp(broker)

@broker.handle("*.info", "workers")
async def base_handler1(logger: Logger):
    logger.info("base_handler1")

@broker.handle("*.info", "workers")
async def base_handler2(logger: Logger):
    logger.info("base_handler2")

@broker.handle("*.error", "workers")
async def base_handler3(logger: Logger):
    logger.info("base_handler3")

@app.after_startup
async def send_messages():
    await broker.publish("", "logs.info")  # handlers: 1 or 2
    await broker.publish("", "logs.info")  # handlers: 1 or 2
    await broker.publish("", "logs.error") # handlers: 3
