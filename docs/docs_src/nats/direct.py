from propan import PropanApp, NatsBroker
from propan.annotations import Logger

broker = NatsBroker()
app = PropanApp(broker)

@broker.handle("test-subj-1", "workers")
async def base_handler1(logger: Logger):
    logger.info("base_handler1")

@broker.handle("test-subj-1", "workers")
async def base_handler2(logger: Logger):
    logger.info("base_handler2")

@broker.handle("test-subj-2", "workers")
async def base_handler3(logger: Logger):
    logger.info("base_handler3")

@app.after_startup
async def send_messages():
    await broker.publish("", "test-subj-1")  # handlers: 1 or 2
    await broker.publish("", "test-subj-1")  # handlers: 1 or 2
    await broker.publish("", "test-subj-2")  # handlers: 3
