import asyncio

import pytest
from aio_pika import Message

from propan.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from propan.rabbit.annotations import RabbitMessage
from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.rabbit
class TestConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_consume_from_exchange(
        self,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitBroker,
    ):
        consume = asyncio.Event()

        @broker.subscriber(queue=queue, exchange=exchange, retry=1)
        def h(m):
            consume.set()

        await broker.start()
        await asyncio.wait(
            (
                asyncio.create_task(
                    broker.publish("hello", queue=queue, exchange=exchange)
                ),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        assert consume.is_set()

    @pytest.mark.asyncio
    async def test_consume_with_get_old(
        self,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitBroker,
    ):
        consume = asyncio.Event()

        await broker.declare_queue(RabbitQueue(queue))
        await broker.declare_exchange(exchange)

        @broker.subscriber(
            queue=RabbitQueue(name=queue, passive=True),
            exchange=RabbitExchange(name=exchange.name, passive=True),
            retry=True,
        )
        def h(m):
            consume.set()

        await broker.start()
        await asyncio.wait(
            (
                asyncio.create_task(
                    broker.publish(
                        Message(b"hello"), queue=queue, exchange=exchange.name
                    )
                ),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        assert consume.is_set()

    @pytest.mark.asyncio
    async def test_consume_ack(
        self,
        queue: str,
        exchange: RabbitExchange,
        full_broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.subscriber(queue=queue, exchange=exchange, retry=1)
        async def handler(msg: RabbitMessage):
            consume.set()

        @full_broker.subscriber(queue=queue + "1", exchange=exchange, retry=1)
        async def handler2(msg: RabbitMessage):
            consume2.set()
            raise ValueError()

        @full_broker.subscriber(queue=queue + "2", exchange=exchange, retry=1)
        async def handler3(msg: RabbitMessage):
            consume3.set()
            raise ValueError()

        await full_broker.start()
        await asyncio.wait(
            (
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue, exchange=exchange)
                ),
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue + "1", exchange=exchange)
                ),
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue + "2", exchange=exchange)
                ),
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
        exchange: RabbitExchange,
        full_broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.subscriber(queue=queue, exchange=exchange, retry=1)
        async def handler(msg: RabbitMessage):
            await msg.raw_message.ack()
            consume.set()

        @full_broker.subscriber(queue=queue + "1", exchange=exchange, retry=1)
        async def handler2(msg: RabbitMessage):
            await msg.raw_message.nack()
            consume2.set()
            raise ValueError()

        @full_broker.subscriber(queue=queue + "2", exchange=exchange, retry=1)
        async def handler3(msg: RabbitMessage):
            await msg.raw_message.reject()
            consume3.set()
            raise ValueError()

        await full_broker.start()
        await asyncio.wait(
            (
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue, exchange=exchange)
                ),
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue + "1", exchange=exchange)
                ),
                asyncio.create_task(
                    full_broker.publish("hello", queue=queue + "2", exchange=exchange)
                ),
                asyncio.create_task(consume.wait()),
                asyncio.create_task(consume2.wait()),
                asyncio.create_task(consume3.wait()),
            ),
            timeout=3,
        )

        assert consume.is_set()
        assert consume2.is_set()
        assert consume3.is_set()
