from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue, ExchangeType

broker = RabbitBroker()
app = PropanApp(broker)

exch = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.HEADERS)

queue_1 = RabbitQueue(
    "test-queue-1", auto_delete=True,
    bind_arguments={ "key": 1 }
)
queue_2 = RabbitQueue(
    "test-queue-2", auto_delete=True,
    bind_arguments={ "key": 2, "key2": 2, "x-match": "any" }
)
queue_3 = RabbitQueue(
    "test-queue-3", auto_delete=True,
    bind_arguments={ "key": 2, "key2": 2, "x-match": "all" }
)

@broker.handle(queue_1, exch)
async def base_handler1(logger: Logger):
    logger.info("base_handler1")

@broker.handle(queue_1, exch)
async def base_handler2(logger: Logger):
    logger.info("base_handler2")

@broker.handle(queue_2, exch)
async def base_handler3(logger: Logger):
    logger.info("base_handler3")

@broker.handle(queue_3, exch)
async def base_handler4(logger: Logger):
    logger.info("base_handler4")

@app.on_startup
async def send_messages():
    await broker.start()

    await broker.publish(exchange=exch, headers={ "key": 1 })  # handlers: 1
    await broker.publish(exchange=exch, headers={ "key": 1 })  # handlers: 2
    await broker.publish(exchange=exch, headers={ "key": 1 })  # handlers: 1
    await broker.publish(exchange=exch, headers={ "key": 2 })  # handlers: 3
    await broker.publish(exchange=exch, headers={ "key2": 2 }) # handlers: 3
    await broker.publish(exchange=exch, headers={ "key": 2,    # handlers: 3, 4
                                                  "key2": 2 })