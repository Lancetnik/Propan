import asyncio
from datetime import datetime
from typing import Dict, List

import pytest
from pydantic import BaseModel, ValidationError

from propan.brokers._model import BrokerUsecase
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
        @test_broker.handle(queue)
        async def handler(m: message_type):
            return m

        r = await test_broker.publish(message, queue, callback=True)

        if expected_message is None:
            expected_message = message

        assert r == expected_message

    @pytest.mark.asyncio
    async def test_handler_calling(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def handler(m: dict):
            return m

        raw_msg = {"msg": "hello!"}
        message = self.build_message(raw_msg, queue)

        wrong_msg = self.build_message("Hi!", queue)

        assert raw_msg == await handler(message)

        await handler(wrong_msg)

        with pytest.raises(ValidationError):
            await handler(wrong_msg, reraise_exc=True)

    @pytest.mark.asyncio
    async def test_rpc_timeout_raises(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def m():  # pragma: no cover
            await asyncio.sleep(1)

        with pytest.raises(asyncio.TimeoutError):
            await test_broker.publish(
                "hello",
                queue,
                callback=True,
                raise_timeout=True,
                callback_timeout=0,
            )

    @pytest.mark.asyncio
    async def test_rpc_timeout(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def m():  # pragma: no cover
            await asyncio.sleep(1)

        r = await test_broker.publish(
            "hello",
            queue,
            callback=True,
            callback_timeout=0,
        )

        assert r is None
