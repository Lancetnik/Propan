import asyncio

import pytest

from propan.brokers import RabbitBroker


@pytest.mark.asyncio
async def test_different_consumers_has_different_messages(context, broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    message1 = None

    async def consumer1(body, message):
        nonlocal message1
        message1 = message

    broker.handle("test_different_consume_1")(consumer1)
    
    message2 = None

    async def consumer2(body, message):
        nonlocal message2
        message2 = message

    broker.handle("test_different_consume_2")(consumer2)

    await broker.start()

    await broker.publish_message(message="hello1", queue="test_different_consume_1")
    await broker.publish_message(message="hello2", queue="test_different_consume_2")

    tries = 0
    while tries < 20:
        await asyncio.sleep(0.1)
        if message1 and message2:
            break
        else:
            tries += 1
    
    assert message1
    assert message2
    assert message1 != message2
    assert context.context["message"] is None
