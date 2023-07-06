import asyncio

import pytest

from tests.brokers.base.consume import BrokerConsumeTestcase
from propan.brokers.nats.nats_js_broker import NatsJSBroker
from propan.annotations import NatsMessage


@pytest.mark.nats
class TestNatsJSConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_consume_with_ack_first(
        self,
        queue: str,
        full_broker: NatsJSBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.handle(queue)
        async def handler(msg: NatsMessage):
            await msg.ack()
            consume.set()

        @full_broker.handle(queue + "1")
        async def handler2(msg: NatsMessage):
            await msg.nak()
            consume2.set()

        @full_broker.handle(queue + "2")
        async def handler3(msg: NatsMessage):
            await msg.term()
            consume3.set()

        async with full_broker:
            await full_broker.start()
            await asyncio.wait((
                asyncio.create_task(full_broker.publish("hello", queue)),
                asyncio.create_task(full_broker.publish("hello", queue + "1")),
                asyncio.create_task(full_broker.publish("hello", queue + "2")),
                asyncio.create_task(consume.wait()),
                asyncio.create_task(consume2.wait()),
                asyncio.create_task(consume3.wait()),
            ), timeout=3)

        assert consume.is_set()
        assert consume2.is_set()
        assert consume3.is_set()
