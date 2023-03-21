import asyncio

import pytest
from aio_pika import IncomingMessage
from propan.brokers import RabbitBroker
from typing import Optional


async def wait_for_message(message):
    tries = 0
    while tries < 10:
        tries += 1
        await asyncio.sleep(0.1)
        if message is not None:
            return
        else:
            break


@pytest.mark.asyncio
async def test_consume(broker: RabbitBroker, settings):
    message: Optional[IncomingMessage] = None

    async def consumer(m):
        nonlocal message
        message = m

    broker.handle(settings.queue)(consumer)
    await broker.start()

    await broker.publish_message(message="hello", queue=settings.queue)

    await wait_for_message(message)

    assert message is not None, "Message not reseaved"
