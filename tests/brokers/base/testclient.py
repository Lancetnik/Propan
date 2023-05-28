import asyncio
from typing import Any

import pytest
from pydantic import ValidationError, create_model

from propan.brokers._model import BrokerUsecase
from propan.types import AnyCallable


class BrokerTestclientTestcase:
    build_message: AnyCallable

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
    async def test_rpc(self, message: Any, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def handler(m):
            return m

        async with test_broker:
            await test_broker.start()
            r = await test_broker.publish(message, queue, callback=True)

        assert r == message

    @pytest.mark.asyncio
    async def test_handler_calling(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def handler(m: dict):
            return m

        raw_msg = {"msg": "hello!"}
        message = self.build_message(raw_msg, queue)

        wrong_msg = self.build_message("Hi!", queue)

        async with test_broker:
            await test_broker.start()
            assert raw_msg == await handler(message)

            await handler(wrong_msg)

            with pytest.raises(ValidationError):
                await handler(wrong_msg, reraise_exc=True)

    @pytest.mark.asyncio
    async def test_rpc_timeout_raises(self, queue: str, test_broker: BrokerUsecase):
        @test_broker.handle(queue)
        async def m():  # pragma: no cover
            await asyncio.sleep(1)

        async with test_broker:
            await test_broker.start()

            with pytest.raises(asyncio.TimeoutError):
                await test_broker.publish(
                    "hello",
                    queue,
                    callback=True,
                    raise_timeout=True,
                    callback_timeout=0,
                )
