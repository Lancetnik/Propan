import asyncio

import pytest

from propan.annotations import NatsMessage
from propan.brokers.nats.nats_js_broker import NatsJSBroker
from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.nats
class TestNatsJSConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_consume_ack(
        self,
        queue: str,
        full_broker: NatsJSBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.handle(queue, retry=1)
        async def handler(msg: NatsMessage):
            consume.set()
            raise ValueError()

        @full_broker.handle(queue + "1", retry=1)
        async def handler2(msg: NatsMessage):
            consume2.set()
            raise ValueError()

        @full_broker.handle(queue + "2", retry=1)
        async def handler3(msg: NatsMessage):
            consume3.set()
            raise ValueError()

        async with full_broker:
            await full_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(full_broker.publish("hello", queue)),
                    asyncio.create_task(full_broker.publish("hello", queue + "1")),
                    asyncio.create_task(full_broker.publish("hello", queue + "2")),
                    asyncio.create_task(consume.wait()),
                    asyncio.create_task(consume2.wait()),
                    asyncio.create_task(consume3.wait()),
                ),
                timeout=3,
            )

        assert consume.is_set()
        assert consume2.is_set()
        assert consume3.is_set()

    @pytest.mark.asyncio
    async def test_consume_manual_ack(
        self,
        queue: str,
        full_broker: NatsJSBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.handle(queue, retry=1)
        async def handler(msg: NatsMessage):
            await msg.ack()
            consume.set()
            raise ValueError()

        @full_broker.handle(queue + "1", retry=1)
        async def handler2(msg: NatsMessage):
            await msg.nak()
            consume2.set()
            raise ValueError()

        @full_broker.handle(queue + "2", retry=1)
        async def handler3(msg: NatsMessage):
            await msg.term()
            consume3.set()
            raise ValueError()

        async with full_broker:
            await full_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(full_broker.publish("hello", queue)),
                    asyncio.create_task(full_broker.publish("hello", queue + "1")),
                    asyncio.create_task(full_broker.publish("hello", queue + "2")),
                    asyncio.create_task(consume.wait()),
                    asyncio.create_task(consume2.wait()),
                    asyncio.create_task(consume3.wait()),
                ),
                timeout=3,
            )

        assert consume.is_set()
        assert consume2.is_set()
        assert consume3.is_set()
