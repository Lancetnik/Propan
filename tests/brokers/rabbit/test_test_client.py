import asyncio
from unittest.mock import Mock

import pytest

from propan.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue
from propan.rabbit.annotations import RabbitMessage
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestRabbitTestclient(BrokerTestclientTestcase):
    @pytest.mark.asyncio
    async def test_raw(
        self,
        test_broker: RabbitBroker,
        queue: str,
    ):
        @test_broker.subscriber(queue)
        async def handler(m):
            raise ValueError()

        await test_broker.start()

        with pytest.raises(ValueError):
            await test_broker.publish("", queue)

    @pytest.mark.asyncio
    async def test_direct(
        self,
        test_broker: RabbitBroker,
        queue: str,
    ):
        @test_broker.subscriber(queue)
        async def handler(m):
            return 1

        @test_broker.subscriber(queue + "1", exchange="test")
        async def handler2(m):
            return 2

        assert 1 == await test_broker.publish("", queue, rpc=True)
        assert 2 == await test_broker.publish(
            "", queue + "1", exchange="test", rpc=True
        )
        assert None is await test_broker.publish("", exchange="test2", rpc=True)

    @pytest.mark.asyncio
    async def test_fanout(
        self,
        test_broker: RabbitBroker,
        queue: str,
    ):
        mock = Mock()

        exch = RabbitExchange("test", type=ExchangeType.FANOUT)

        @test_broker.subscriber(queue, exchange=exch)
        async def handler(m):
            mock()

        await test_broker.publish("", exchange=exch, rpc=True)
        assert None is await test_broker.publish("", exchange="test2", rpc=True)

        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_topic(
        self,
        test_broker: RabbitBroker,
    ):
        exch = RabbitExchange("test", type=ExchangeType.TOPIC)

        @test_broker.subscriber("*.info", exchange=exch)
        async def handler(m):
            return 1

        @test_broker.subscriber("*.error", exchange=exch)
        async def handler2(m):
            return 2

        assert 1 == await test_broker.publish("", "logs.info", exchange=exch, rpc=True)
        assert 2 == await test_broker.publish("", "logs.error", exchange=exch, rpc=True)
        assert None is await test_broker.publish("", "logs.error", rpc=True)

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
        q3 = RabbitQueue(
            "test-queue-4",
            bind_arguments={},
        )
        exch = RabbitExchange("exchange", type=ExchangeType.HEADERS)

        @test_broker.subscriber(q2, exch)
        async def handler2():
            return 2

        @test_broker.subscriber(q1, exch)
        async def handler():
            return 1

        @test_broker.subscriber(q3, exch)
        async def handler3():
            return 3

        assert 2 == await test_broker.publish(
            exchange=exch, rpc=True, headers={"key": 2, "key2": 2}
        )
        assert 1 == await test_broker.publish(
            exchange=exch, rpc=True, headers={"key": 2}
        )
        assert 3 == await test_broker.publish(exchange=exch, rpc=True, headers={})

    @pytest.mark.asyncio
    async def test_consume_manual_ack(
        self,
        queue: str,
        exchange: RabbitExchange,
        test_broker: RabbitBroker,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        consume3 = asyncio.Event()

        @test_broker.subscriber(queue=queue, exchange=exchange, retry=1)
        async def handler(msg: RabbitMessage):
            await msg.raw_message.ack()
            consume.set()

        @test_broker.subscriber(queue=queue + "1", exchange=exchange, retry=1)
        async def handler2(msg: RabbitMessage):
            await msg.raw_message.nack()
            consume2.set()
            raise ValueError()

        @test_broker.subscriber(queue=queue + "2", exchange=exchange, retry=1)
        async def handler3(msg: RabbitMessage):
            await msg.raw_message.reject()
            consume3.set()
            raise ValueError()

        async with test_broker:
            await test_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(
                        test_broker.publish("hello", queue=queue, exchange=exchange)
                    ),
                    asyncio.create_task(
                        test_broker.publish(
                            "hello", queue=queue + "1", exchange=exchange
                        )
                    ),
                    asyncio.create_task(
                        test_broker.publish(
                            "hello", queue=queue + "2", exchange=exchange
                        )
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
