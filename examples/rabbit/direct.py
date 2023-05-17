from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue

broker = RabbitBroker()
app = PropanApp(broker)

direct_exchange = RabbitExchange("exchange", auto_delete=True)
queue_1 = RabbitQueue("test-queue-1", auto_delete=True)
queue_2 = RabbitQueue("test-queue-2", auto_delete=True)


@broker.handle(queue_1, direct_exchange)
async def base_handler1(logger: Logger):
    logger.info("base_handler1")


@broker.handle(queue_1, direct_exchange)
async def base_handler2(logger: Logger):
    logger.info("base_handler2")


@broker.handle(queue_2, direct_exchange)
async def base_handler3(logger: Logger):
    logger.info("base_handler3")


@app.after_startup
async def send_messages():
    await broker.publish(queue=queue_1, exchange=direct_exchange)
    await broker.publish(queue=queue_1, exchange=direct_exchange)
    await broker.publish(queue=queue_1, exchange=direct_exchange)
    await broker.publish(queue=queue_2, exchange=direct_exchange)
