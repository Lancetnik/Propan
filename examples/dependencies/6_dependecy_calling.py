"""
Depends parameter allows to call function before
natural handler with providing all arguments and context
inside dependency function
"""
from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.utils import Depends, use_context

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@use_context
async def async_dependency(body, logger):
    logger.info(f"Async calls with: {body}")
    return True


def sync_dependency():
    print("Hello, i am here!")
    return True


@broker.handle("test")
async def base_handler(
    body: dict,
    async_called: bool = Depends(async_dependency),
    sync_called: bool = Depends(sync_dependency),
):
    assert async_called and sync_called
