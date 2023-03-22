import asyncio

import pytest

from propan.brokers import RabbitBroker


@pytest.mark.asyncio
async def test_consume(broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()
    was_called = [False]
    await _test_consume(broker, "test", was_called)
    await broker.start()
    await _wait_for_message(was_called)
    assert was_called[0], "Message not reseaved"


@pytest.mark.asyncio
async def test_different_consume(broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    was_called_1 = [False]
    await _test_consume(broker, "test1", was_called_1)

    was_called_2 = [False]
    await _test_consume(broker, "test2", was_called_2)
    await broker.start()

    await _wait_for_message(was_called_1)
    assert was_called_1[0], "Message1 not reseaved"

    await _wait_for_message(was_called_2)
    assert was_called_2[0], "Message2 not reseaved"


@pytest.mark.asyncio
async def test_same_consume(broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    with pytest.raises(ValueError):
        broker.handle("test")(lambda: None)
        broker.handle("test")(lambda: None)


async def _test_consume(broker, queue, was_called):
    async def consumer(body):
        was_called[0] = body

    broker.handle(queue)(consumer)
    await broker.publish_message(message="hello", queue=queue)


async def _wait_for_message(message, max_tries=20):
    tries = 0
    while tries < max_tries:
        await asyncio.sleep(0.1)
        if message[0] is not False:
            return
        else:
            tries += 1
