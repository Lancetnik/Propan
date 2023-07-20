from propan import PropanApp
from propan.annotations import Logger
from propan.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)


@broker.subscriber("test-queue")
@broker.subscriber("another-qeue")
@broker.publisher("response-queue")
@broker.publisher("another-response-queue")
async def handle(msg, logger: Logger):
    logger.info(msg)
