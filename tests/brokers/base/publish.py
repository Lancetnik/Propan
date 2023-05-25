from asyncio import Event, wait_for
from typing import Any
from unittest.mock import Mock

import pytest
from pydantic import create_model

from propan.brokers.model import BrokerUsecase


class BrokerPublishTestcase:
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
    async def test_rpc(
        self, message: Any, mock: Mock, queue: str, broker: BrokerUsecase
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @broker.handle(queue)
        async def handler(m):
            mock(m)

        async with broker:
            await broker.start()
            await broker.publish(message, queue)
            await wait_for(consume.wait(), 3)

        mock.assert_called_with(message)
