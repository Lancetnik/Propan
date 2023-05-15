import asyncio

import pytest
from pydantic import create_model

from propan import RedisBroker


@pytest.mark.asyncio
@pytest.mark.redis
@pytest.mark.parametrize(
    "message",
    (
        b"hello!",
        "hello",
        {"message": "hello!"},
        create_model("Message", r=str)(r="hello!"),
        [1, 2, 3],
    ),
)
async def test_rpc(message, channel_name: str, broker: RedisBroker):
    @broker.handle(channel_name)
    async def handler(m):
        return m

    async with broker:
        await broker.start()
        r = await broker.publish(message, channel_name, callback=True)

    assert r == message


@pytest.mark.asyncio
@pytest.mark.redis
async def test_rpc_timeout_raises(channel_name: str, full_broker: RedisBroker):
    @full_broker.handle(channel_name)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with full_broker:
        await full_broker.start()

        with pytest.raises(asyncio.TimeoutError):  # pragma: no branch
            await full_broker.publish(
                message="hello",
                channel=channel_name,
                callback=True,
                raise_timeout=True,
                callback_timeout=0,
            )


@pytest.mark.asyncio
@pytest.mark.redis
async def test_rpc_timeout_none(channel_name: str, full_broker: RedisBroker):
    @full_broker.handle(channel_name)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with full_broker:
        await full_broker.start()

        r = await full_broker.publish(
            message="hello",
            channel=channel_name,
            callback=True,
            callback_timeout=0,
        )

    assert r is None
