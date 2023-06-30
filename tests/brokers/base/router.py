import pytest

from propan.brokers._model import BrokerAsyncUsecase, BrokerRouter
from propan.types import AnyCallable


@pytest.mark.asyncio
class RouterTestcase:
    build_message: AnyCallable

    async def test_empty_prefix(
        self,
        router: BrokerRouter,
        test_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        @router.handle(queue)
        async def handler(m):
            return m

        test_broker.include_router(router)

        r = await test_broker.publish(
            "test",
            queue,
            callback=True,
        )

        assert r == "test"

    async def test_not_empty_prefix(
        self,
        router: BrokerRouter,
        test_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test/"

        @router.handle(queue)
        async def handler(m):
            return m

        test_broker.include_router(router)

        r = await test_broker.publish(
            "test",
            f"test/{queue}",
            callback=True,
        )

        assert r == "test"

    async def test_router_testing(
        self,
        router: BrokerRouter,
        test_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test/"

        @router.handle(queue)
        async def handler(m):
            return m

        test_broker.include_router(router)

        message = self.build_message("hi", queue)

        assert await handler(message, True) == "hi"
