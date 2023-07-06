import asyncio
from unittest.mock import Mock

import pytest
from aio_pika import Message

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from propan.annotations import RabbitMessage
from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.rabbit
class TestRabbitConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_consume_from_exchange(
        self,
        mock: Mock,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch
        broker.handle(queue=queue, exchange=exchange, retry=1)(mock)

        async with broker:
            await broker.start()
            await asyncio.wait((
                asyncio.create_task(broker.publish("hello", queue=queue, exchange=exchange)),
                asyncio.create_task(consume.wait()),
            ), timeout=3)

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_with_get_old(
        self,
        mock: Mock,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        await broker.connect()
        await broker.declare_queue(RabbitQueue(queue))
        await broker.declare_exchange(exchange)

        broker.handle(
            queue=RabbitQueue(name=queue, passive=True),
            exchange=RabbitExchange(name=exchange.name, passive=True),
            retry=True,
        )(mock)

        async with broker:
            await broker.start()
            await asyncio.wait((
                asyncio.create_task(broker.publish(Message(b"hello"), queue=queue, exchange=exchange.name)),
                asyncio.create_task(consume.wait()),
            ), timeout=3)

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_with_ack_first(
        self,
        queue: str,
        exchange: RabbitExchange,
        full_broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @full_broker.handle(queue=queue, exchange=exchange, retry=1)
        async def handler(msg: RabbitMessage):
            await msg.ack()
            consume.set()

        @full_broker.handle(queue=queue + "1", exchange=exchange, retry=1)
        async def handler2(msg: RabbitMessage):
            await msg.nack()
            consume2.set()

        @full_broker.handle(queue=queue + "2", exchange=exchange, retry=1)
        async def handler3(msg: RabbitMessage):
            await msg.reject()
            consume3.set()

        async with full_broker:
            await full_broker.start()
            await asyncio.wait((
                asyncio.create_task(full_broker.publish("hello", queue=queue, exchange=exchange)),
                asyncio.create_task(full_broker.publish("hello", queue=queue + "1", exchange=exchange)),
                asyncio.create_task(full_broker.publish("hello", queue=queue + "2", exchange=exchange)),
                asyncio.create_task(consume.wait()),
                asyncio.create_task(consume2.wait()),
                asyncio.create_task(consume3.wait()),
            ), timeout=3)

        assert consume.is_set()
        assert consume2.is_set()
        assert consume3.is_set()
