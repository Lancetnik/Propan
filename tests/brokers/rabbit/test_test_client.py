from unittest.mock import Mock

import pytest

from propan.brokers.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from propan.test.rabbit import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestRabbitTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)

    @pytest.mark.asyncio
    async def test_direct(
        self,
        test_broker: RabbitBroker,
        queue: str,
    ):
        @test_broker.handle(queue)
        async def handler(m):
            return 1

        @test_broker.handle(queue + "1", exchange="test")
        async def handler2(m):
            return 2

        assert 1 == await test_broker.publish("", queue, callback=True)
        assert 2 == await test_broker.publish(
            "", queue + "1", exchange="test", callback=True
        )
        assert None is await test_broker.publish("", exchange="test2", callback=True)

    @pytest.mark.asyncio
    async def test_fanout(
        self,
        test_broker: RabbitBroker,
        queue: str,
    ):
        mock = Mock()

        exch = RabbitExchange("test", type=ExchangeType.FANOUT)

        @test_broker.handle(queue, exchange=exch)
        async def handler(m):
            mock()

        @test_broker.handle(queue + "1", exchange=exch)
        async def handler2(m):
            mock()

        await test_broker.publish("", exchange=exch, callback=True)
        await test_broker.publish("", exchange=exch, callback=True)
        assert None is await test_broker.publish("", exchange="test2", callback=True)

        assert mock.call_count == 2

    @pytest.mark.asyncio
    async def test_topic(
        self,
        test_broker: RabbitBroker,
    ):
        exch = RabbitExchange("test", type=ExchangeType.TOPIC)

        @test_broker.handle("*.info", exchange=exch)
        async def handler(m):
            return 1

        @test_broker.handle("*.error", exchange=exch)
        async def handler2(m):
            return 2

        assert 1 == await test_broker.publish(
            "", "logs.info", exchange=exch, callback=True
        )
        assert 2 == await test_broker.publish(
            "", "logs.error", exchange=exch, callback=True
        )
        assert None is await test_broker.publish("", "logs.error", callback=True)

    @pytest.mark.asyncio
    async def test_header(
        self,
        test_broker: RabbitBroker,
    ):
        q1 = RabbitQueue(
            "test-queue-2",
            bind_arguments={"key": 2, "key2": 2, "x-match": "any"},
        )
        q2 = RabbitQueue(
            "test-queue-3",
            bind_arguments={"key": 2, "key2": 2, "x-match": "all"},
        )
        exch = RabbitExchange("exchange", type=ExchangeType.HEADERS)

        @test_broker.handle(q2, exch)
        async def handler2():
            return 2

        @test_broker.handle(q1, exch)
        async def handler():
            return 1

        assert 2 == await test_broker.publish(
            exchange=exch, callback=True, headers={"key": 2, "key2": 2}
        )
        assert 1 == await test_broker.publish(
            exchange=exch, callback=True, headers={"key": 2}
        )
        assert None is await test_broker.publish(
            exchange=exch, callback=True, headers={}
        )
