from asyncio import Event, wait_for
from unittest.mock import Mock

import pytest
from pydantic import create_model

from propan import KafkaBroker


@pytest.mark.asyncio
@pytest.mark.kafka
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
async def test_rpc(message, mock: Mock, topic: str, broker: KafkaBroker):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    @broker.handle(topic)
    async def handler(m):
        mock(m)

    async with broker:
        await broker.start()
        await broker.publish(message, topic)
        await wait_for(consume.wait(), 3)

    mock.assert_called_with(message)
