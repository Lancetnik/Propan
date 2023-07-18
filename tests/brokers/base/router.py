import asyncio
from unittest.mock import Mock

import pytest

from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.router import BrokerRouter
from propan.types import AnyCallable


@pytest.mark.asyncio
class RouterTestcase:
    build_message: AnyCallable

    async def test_empty_prefix(
        self,
        mock: Mock,
        router: BrokerRouter,
        broker: BrokerAsyncUsecase,
        queue: str,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        def subscriber():
            mock()

        broker.include_router(router)

        await broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(broker.publish("hello", queue)),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()

    async def test_not_empty_prefix(
        self,
        mock: Mock,
        router: BrokerRouter,
        broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test/"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        def subscriber():
            mock()

        broker.include_router(router)

        await broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(broker.publish("hello", f"test/{queue}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()


@pytest.mark.asyncio
class RouterLocalTestcase:
    async def test_test_client(
        self,
        mock: Mock,
        router: BrokerRouter,
        test_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test/"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        def subscriber():
            mock()

        test_broker.include_router(router)

        await test_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(test_broker.publish("hello", f"test/{queue}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()
