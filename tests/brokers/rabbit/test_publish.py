import asyncio

import pytest
from pydantic import create_model

from propan.brokers.rabbit import RabbitBroker, RabbitQueue


@pytest.mark.asyncio
@pytest.mark.rabbit
@pytest.mark.parametrize(
    "message",
    (
        b"hello!",
        "hello",
        {"message": "hello!"},
        create_model("Message", r=str)(r="hello!"),
    ),
)
async def test_rpc(message, queue: RabbitQueue, broker: RabbitBroker):
    @broker.handle(queue)
    async def handler(m):
        return m

    async with broker:
        await broker.start()
        r = await broker.publish(message, queue=queue, callback=True)

    assert r == message


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_rpc_timeout_raises(queue: RabbitQueue, full_broker: RabbitBroker):
    @full_broker.handle(queue)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with full_broker:
        await full_broker.start()

        with pytest.raises(asyncio.TimeoutError):
            await full_broker.publish(
                message="hello",
                queue=queue,
                callback=True,
                raise_timeout=True,
                callback_timeout=0,
            )


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_rpc_timeout(queue: RabbitQueue, full_broker: RabbitBroker):
    @full_broker.handle(queue)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with full_broker:
        await full_broker.start()

        r = await full_broker.publish(
            message="hello",
            queue=queue,
            callback=True,
            callback_timeout=0,
        )

    assert r is None
