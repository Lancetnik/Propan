"""
With Python 3.10+ you can use
typing.Annotated class as a shortcut to Depends and Alias
"""
import logging
from typing import Annotated

from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.utils import Alias, Depends, use_context

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

Logger = Annotated[logging.Logger, Alias("broker.logger")]


@use_context
async def async_dependency(body, logger: Logger):
    logger.info(f"Async calls with: {body}")
    return True


Dependency = Annotated[bool, Depends(async_dependency)]


@broker.handle("test")
async def base_handler(body: dict, async_called: Dependency):
    assert async_called is True
