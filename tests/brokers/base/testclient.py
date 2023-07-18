from datetime import datetime
from typing import Dict, List

import anyio
import pytest
from pydantic import BaseModel

from propan.broker.core.abc import BrokerUsecase
from propan.types import AnyCallable


class SimpleModel(BaseModel):
    r: str


now = datetime.now()


class BrokerTestclientTestcase:
    build_message: AnyCallable

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("message", "message_type", "expected_message"),
        (
            ("hello", str, None),
            (b"hello", bytes, None),
            (1, int, None),
            (1.0, float, None),
            (False, bool, None),
            ({"m": 1}, Dict[str, int], None),
            ([1, 2, 3], List[int], None),
            (SimpleModel(r="hello!"), SimpleModel, None),
            (SimpleModel(r="hello!"), dict, {"r": "hello!"}),
            (now, datetime, now),
        ),
    )
    async def test_serialize(
        self,
        test_broker: BrokerUsecase,
        queue: str,
        message,
        message_type,
        expected_message,
    ):
        @test_broker.subscriber(queue)
        async def handler(m: message_type):
            return m

        r = await test_broker.publish(message, queue, rpc=True)

        if expected_message is None:
            expected_message = message

        assert r == expected_message

    @pytest.mark.asyncio
    async def test_rpc_timeout_raises(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.subscriber(queue)
        async def m():  # pragma: no cover
            await anyio.sleep(1)

        with pytest.raises(TimeoutError):
            await test_broker.publish(
                "hello",
                queue,
                rpc=True,
                raise_timeout=True,
                rpc_timeout=0,
            )

    @pytest.mark.asyncio
    async def test_rpc_timeout(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.subscriber(queue)
        async def m():  # pragma: no cover
            await anyio.sleep(1)

        r = await test_broker.publish(
            "hello",
            queue,
            rpc=True,
            rpc_timeout=0,
        )

        assert r is None
