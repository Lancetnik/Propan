from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitQueue

broker = RabbitBroker(consumers=10)
app = PropanApp(broker)

queue = RabbitQueue(
    name="test",
    durable=True,
    arguments={
        "x-queue-type": "stream",
    },
)


@broker.handle(queue, consume_arguments={"x-stream-offset": "first"})
async def handle(msg, logger: Logger):
    logger.info(msg)


@app.after_startup
async def test():
    await broker.publish("Hi!", queue)
