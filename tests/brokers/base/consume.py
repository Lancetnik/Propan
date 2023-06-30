from asyncio import Event, wait_for
from unittest.mock import Mock

import pytest

from propan.brokers._model import BrokerAsyncUsecase


class BrokerConsumeTestcase:
    @pytest.mark.asyncio
    async def test_consume(
        self,
        mock: Mock,
        queue: str,
        broker: BrokerAsyncUsecase,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle(queue)(mock)
            await broker.start()
            await broker.publish("hello", queue)
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_double(
        self,
        mock: Mock,
        queue: str,
        broker: BrokerAsyncUsecase,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle(queue)(mock)
            await broker.start()

            await broker.publish("hello", queue)
            await wait_for(consume.wait(), 3)

            consume.clear()
            await broker.publish("hello", queue)
            await wait_for(consume.wait(), 3)

        assert mock.call_count == 2

    @pytest.mark.asyncio
    async def test_different_consume(
        self,
        mock: Mock,
        queue: str,
        broker: BrokerAsyncUsecase,
    ):
        first_consume = Event()
        second_consume = Event()

        mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
        mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

        another_topic = queue + "1"
        async with broker:
            broker.handle(queue)(mock.method)
            broker.handle(another_topic)(mock.method2)
            await broker.start()

            await broker.publish("hello", queue)
            await broker.publish("hello", another_topic)

            await wait_for(first_consume.wait(), 3)
            await wait_for(second_consume.wait(), 3)

        mock.method.assert_called_once()
        mock.method2.assert_called_once()
