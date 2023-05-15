import asyncio

import pytest
from pydantic import ValidationError, create_model

from propan import RedisBroker
from propan.test.redis import build_message


@pytest.mark.asyncio
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
async def test_rpc(message, channel_name: str, test_broker: RedisBroker):
    @test_broker.handle(channel_name)
    async def handler(m):
        return m

    async with test_broker:
        await test_broker.start()
        r = await test_broker.publish(message, channel_name, callback=True)

    assert r == message


@pytest.mark.asyncio
async def test_rpc_timeout_raises(channel_name: str, test_broker: RedisBroker):
    @test_broker.handle(channel_name)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with test_broker:
        await test_broker.start()

        with pytest.raises(asyncio.TimeoutError):
            await test_broker.publish(
                message="hello",
                channel=channel_name,
                callback=True,
                raise_timeout=True,
                callback_timeout=0,
            )


@pytest.mark.asyncio
async def test_pattern_consume(channel_name: str, test_broker: RedisBroker):
    @test_broker.handle(".*", pattern=True)
    async def m():  # pragma: no cover
        return 1

    async with test_broker:
        await test_broker.start()

        assert (
            await test_broker.publish(
                message="hello",
                channel=channel_name,
                callback=True,
            )
        ) == 1


@pytest.mark.asyncio
async def test_handler_calling(channel_name: str, test_broker: RedisBroker):
    @test_broker.handle(channel_name)
    async def handler(m: dict):
        return m

    raw_msg = {"msg": "hello!"}
    message = build_message(raw_msg, channel_name)

    wrong_msg = build_message("Hi!", channel_name)

    async with test_broker:
        await test_broker.start()
        assert raw_msg == await handler(message)

        await handler(wrong_msg)

        with pytest.raises(ValidationError):
            await handler(wrong_msg, reraise_exc=True)
