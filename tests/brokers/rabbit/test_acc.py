import asyncio

import pytest
from aio_pika import IncomingMessage
from propan.brokers import RabbitBroker
from typing import Optional

from loguru import logger


async def fake_handle(self, message: IncomingMessage) -> None:
    queue_name = message.routing_key
    async with message.process():
        await self.handlers[queue_name](message)


@pytest.fixture
def patched_broker(broker: RabbitBroker) -> RabbitBroker:
    broker._handle_message = fake_handle
    yield broker


@pytest.mark.asyncio
async def test_consume(patched_broker: RabbitBroker, settings):
    message: Optional[IncomingMessage] = None

    async def consumer(m):
        nonlocal message
        message = m

    patched_broker.handlers[settings.queue] = consumer
    await patched_broker.start()

    await patched_broker.publish_message(settings.queue, "hello")
    while message is None:
        await asyncio.sleep(0.1)

    logger.debug(message)
