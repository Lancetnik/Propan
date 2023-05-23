import pytest
from pydantic import ValidationError, create_model

from propan import KafkaBroker
from propan.test.kafka import build_message


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
async def test_rpc(message, topic: str, test_broker: KafkaBroker):
    @test_broker.handle(topic)
    async def handler(m):
        return m

    async with test_broker:
        await test_broker.start()
        r = await test_broker.publish(message, topic, callback=True)

    assert r == message


@pytest.mark.asyncio
async def test_handler_calling(topic: str, test_broker: KafkaBroker):
    @test_broker.handle(topic)
    async def handler(m: dict):
        return m

    raw_msg = {"msg": "hello!"}
    message = build_message(raw_msg, topic)

    wrong_msg = build_message("Hi!", topic)

    async with test_broker:
        await test_broker.start()
        assert raw_msg == await handler(message)

        await handler(wrong_msg)

        with pytest.raises(ValidationError):
            await handler(wrong_msg, reraise_exc=True)
