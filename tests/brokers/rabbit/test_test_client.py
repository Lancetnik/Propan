import asyncio

import pytest
from pydantic import ValidationError, create_model

from propan.brokers.rabbit import RabbitBroker, RabbitQueue
from propan.test.rabbit import build_message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    (
        b"hello!",
        "hello",
        {"message": "hello!"},
        create_model("Message", r=str)(r="hello!"),
    ),
)
async def test_rpc(message, queue: RabbitQueue, test_broker: RabbitBroker):
    @test_broker.handle(queue)
    async def handler(m):
        return m

    async with test_broker:
        await test_broker.start()
        r = await test_broker.publish(message, queue=queue, callback=True)

    assert r == message


@pytest.mark.asyncio
async def test_rpc_timeout_raises(queue: RabbitQueue, test_broker: RabbitBroker):
    @test_broker.handle(queue)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with test_broker:
        await test_broker.start()

        with pytest.raises(asyncio.TimeoutError):
            await test_broker.publish(
                message="hello",
                queue=queue,
                callback=True,
                raise_timeout=True,
                callback_timeout=0,
            )


@pytest.mark.asyncio
async def test_rpc_timeout(queue: RabbitQueue, test_broker: RabbitBroker):
    @test_broker.handle(queue)
    async def m():  # pragma: no cover
        await asyncio.sleep(1)

    async with test_broker:
        await test_broker.start()

        r = await test_broker.publish(
            message="hello",
            queue=queue,
            callback=True,
            callback_timeout=0,
        )

    assert r is None


@pytest.mark.asyncio
async def test_handler_calling(queue: RabbitQueue, test_broker: RabbitBroker):
    @test_broker.handle(queue)
    async def handler(m: dict):
        return m

    raw_msg = {"msg": "hello!"}
    message = build_message(raw_msg, queue)

    wrong_msg = build_message("Hi!", queue)

    async with test_broker:
        await test_broker.start()
        assert raw_msg == await handler(message)

        await handler(wrong_msg)

        with pytest.raises(ValidationError):
            await handler(wrong_msg, reraise_exc=True)
