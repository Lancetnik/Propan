from asyncio import Event, wait_for
from unittest.mock import Mock

import pytest

from propan import RedisBroker
from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.redis
class TestRedisConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_pattern_consume(
        self,
        mock: Mock,
        queue: str,
        broker: RedisBroker,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle("*", pattern=True)(mock)
            await broker.start()
            await broker.publish("hello", queue)
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_from_native_redis(
        self,
        mock: Mock,
        queue: str,
        broker: RedisBroker,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle(queue)(mock)
            await broker.start()
            await broker._connection.publish(queue, "msg")
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()
