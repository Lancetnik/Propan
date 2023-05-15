from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue

broker = RabbitBroker()
app = PropanApp(broker)

exch = RabbitExchange("exchange", auto_delete=True)

queue_1 = RabbitQueue("test-q-1", auto_delete=True)
queue_2 = RabbitQueue("test-q-2", auto_delete=True)

@broker.handle(queue_1, exch)
async def base_handler1(logger: Logger):
    logger.info("base_handler1")

@broker.handle(queue_1, exch)
async def base_handler2(logger: Logger):
    logger.info("base_handler2")

@broker.handle(queue_2, exch)
async def base_handler3(logger: Logger):
    logger.info("base_handler3")

@app.on_startup
async def send_messages():
    await broker.start()

    await broker.publish(queue="test-q-1", exchange=exch)  # handlers: 1
    await broker.publish(queue="test-q-1", exchange=exch)  # handlers: 2
    await broker.publish(queue="test-q-1", exchange=exch)  # handlers: 1
    await broker.publish(queue="test-q-2", exchange=exch)  # handlers: 3