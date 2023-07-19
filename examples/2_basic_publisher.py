from propan import PropanApp
from propan.rabbit import RabbitBroker
from propan.annotations import Logger

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)


@broker.subscriber("test-queue")
@broker.publisher("response-queue")
async def handle(msg, logger: Logger):
    logger.info(msg)


@broker.subscriber("response-queue")
async def process_response(msg, logger: Logger):
    logger.info(f"Process response: {msg}")


@app.after_startup
async def test_publishing():
    await broker.publish("Hello!", "test-queue")
