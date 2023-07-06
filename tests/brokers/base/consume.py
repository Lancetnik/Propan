import asyncio
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
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        broker.handle(queue)(mock)

        async with broker:
            await broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(broker.publish("hello", queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_double(
        self,
        mock: Mock,
        queue: str,
        broker: BrokerAsyncUsecase,
    ):
        consume = asyncio.Event()
        consume2 = asyncio.Event()

        @broker.handle(queue)
        async def handler(m):
            if not consume.is_set():
                consume.set()
            else:
                consume2.set()
            mock()

        async with broker:
            await broker.start()

            await asyncio.wait(
                (
                    asyncio.create_task(broker.publish("hello", queue)),
                    asyncio.create_task(broker.publish("hello", queue)),
                    asyncio.create_task(consume.wait()),
                    asyncio.create_task(consume2.wait()),
                ),
                timeout=3,
            )

        assert mock.call_count == 2

    @pytest.mark.asyncio
    async def test_different_consume(
        self,
        mock: Mock,
        queue: str,
        broker: BrokerAsyncUsecase,
    ):
        first_consume = asyncio.Event()
        second_consume = asyncio.Event()

        mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
        mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

        another_topic = queue + "1"
        broker.handle(queue)(mock.method)
        broker.handle(another_topic)(mock.method2)

        async with broker:
            await broker.start()

            await asyncio.wait(
                (
                    asyncio.create_task(broker.publish("hello", queue)),
                    asyncio.create_task(broker.publish("hello", another_topic)),
                    asyncio.create_task(first_consume.wait()),
                    asyncio.create_task(second_consume.wait()),
                ),
                timeout=3,
            )

        mock.method.assert_called_once()
        mock.method2.assert_called_once()
