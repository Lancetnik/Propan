"""
@use_context decorator allows pass context dependencies
to all functions with the same context through the functions
calling stack.
"""
import aio_pika
from propan.app import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.utils import use_context

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body: dict):
    await nested_funcion()


@use_context
async def nested_funcion(logger, message: aio_pika.Message):
    logger.info(f"Message `{message}` processing")
