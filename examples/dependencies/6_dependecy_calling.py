"""
Depends parameter allows to call function before
natural handler with providing all arguments and context
inside dependency function

Dependecies argument names should be calling same as a handler arguments
Dependency decorated by `use_context` as a default if hanler was decorated
"""
from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.utils import Depends

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


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
