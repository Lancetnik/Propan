import asyncio

import pytest

from propan.brokers import RabbitBroker, RabbitQueue


@pytest.mark.asyncio
async def test_consume(queue: RabbitQueue, broker: RabbitBroker):
    async with broker:
        was_called = [False]
        await _test_consume(broker, queue, was_called)        
        await _wait_for_message(was_called)
        assert was_called[0], "Message not reseaved"


@pytest.mark.asyncio
async def test_different_consume(queue: RabbitQueue, broker: RabbitBroker):
    async with broker:
        was_called_1 = [False]
        await _test_consume(broker, queue, was_called_1)

        was_called_2 = [False]
        await _test_consume(broker,
                            RabbitQueue(**queue.dict(exclude={"name"}), name=queue.name+"1"),
                            was_called_2)

        await _wait_for_message(was_called_1)
        assert was_called_1[0], "Message1 not reseaved"

        await _wait_for_message(was_called_2)
        assert was_called_2[0], "Message2 not reseaved"


@pytest.mark.asyncio
async def test_same_consume(queue: RabbitQueue, broker: RabbitBroker):
    with pytest.raises(ValueError):
        broker.handle(queue)(lambda: None)
        broker.handle(queue)(lambda: None)


async def _test_consume(broker: RabbitBroker, queue: RabbitQueue, was_called: bool):
    async def consumer(body):
        was_called[0] = body

    broker.handle(queue)(consumer)
    await broker.start()
    await broker.publish_message(message="hello", queue=queue)


async def _wait_for_message(message, max_tries=40):
    tries = 0
    while tries < max_tries:
        await asyncio.sleep(0.1)
        if message[0] is not False:
            return
        else:
            tries += 1
    return message[0]
