"""
@apply_types decorator allows pass context dependencies
to all functions with the same context through the functions
calling stack.
"""
from propan import PropanApp, RabbitBroker, apply_types
from propan.annotations import Logger, RabbitMessage

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body: dict):
    await nested_funcion()


@apply_types
async def nested_funcion(logger: Logger, message: RabbitMessage):
    logger.info(f"Message `{message}` processing")
