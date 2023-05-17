from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue, ExchangeType

broker = RabbitBroker()
app = PropanApp(broker)

exch = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.TOPIC)

queue_1 = RabbitQueue("test-queue-1", auto_delete=True, routing_key="*.info")
queue_2 = RabbitQueue("test-queue-2", auto_delete=True, routing_key="*.debug")

@broker.handle(queue_1, exch)
async def base_handler1(logger: Logger):
    logger.info("base_handler1")

@broker.handle(queue_1, exch)
async def base_handler2(logger: Logger):
    logger.info("base_handler2")

@broker.handle(queue_2, exch)
async def base_handler3(logger: Logger):
    logger.info("base_handler3")

@app.after_startup
async def send_messages():
    await broker.publish(routing_key="logs.info", exchange=exch)  # handlers: 1
    await broker.publish(routing_key="logs.info", exchange=exch)  # handlers: 2
    await broker.publish(routing_key="logs.info", exchange=exch)  # handlers: 1
    await broker.publish(routing_key="logs.debug", exchange=exch) # handlers: 3