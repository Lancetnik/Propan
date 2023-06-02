from asyncio import Event, wait_for
from unittest.mock import Mock

import pytest
from aio_pika import Message

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
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
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle(queue=queue, exchange=exchange, retry=1)(mock)
            await broker.start()
            await broker.publish({"msg": "hello"}, queue=queue, exchange=exchange)
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_with_get_old(
        self,
        mock: Mock,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitBroker,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        await broker.connect()
        await broker._init_queue(RabbitQueue(queue))
        await broker._init_exchange(exchange)

        broker.handle(
            queue=RabbitQueue(name=queue, passive=True),
            exchange=RabbitExchange(name=exchange.name, passive=True),
            retry=True,
        )(mock)

        async with broker:
            await broker.start()
            await broker.publish(Message(b"hello"), queue=queue, exchange=exchange.name)
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()
