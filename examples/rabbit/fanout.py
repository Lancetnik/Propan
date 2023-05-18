from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import ExchangeType, RabbitExchange, RabbitQueue

broker = RabbitBroker()
app = PropanApp(broker)

fanout_exchange = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.FANOUT)
queue_1 = RabbitQueue("test-queue-1", auto_delete=True)
queue_2 = RabbitQueue("test-queue-2", auto_delete=True)


@broker.handle(queue_1, fanout_exchange)
async def base_handler1(logger: Logger):
    logger.info("base_handler1")


@broker.handle(queue_1, fanout_exchange)
async def base_handler2(logger: Logger):
    logger.info("base_handler2")


@broker.handle(queue_2, fanout_exchange)
async def base_handler3(logger: Logger):
    logger.info("base_handler3")


@app.after_startup
async def send_messages():
    await broker.publish(exchange=fanout_exchange)
    await broker.publish(exchange=fanout_exchange)
    await broker.publish(exchange=fanout_exchange)
    await broker.publish(exchange=fanout_exchange)
