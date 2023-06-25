import pytest

from propan.brokers._model import BrokerRouter, BrokerUsecase


@pytest.mark.asyncio
class RouterTestcase:
    async def test_empty_prefix(
        self,
        router: BrokerRouter,
        test_broker: BrokerUsecase,
        queue: str,
    ):
        @router.handle(queue)
        async def handler(m):
            return m

        test_broker.include_router(router)

        async with test_broker:
            await test_broker.start()
            r = await test_broker.publish(
                "test",
                queue,
                callback=True,
            )

        assert r == "test"

    async def test_not_empty_prefix(
        self,
        router: BrokerRouter,
        test_broker: BrokerUsecase,
        queue: str,
    ):
        router.prefix = "test/"

        @router.handle(queue)
        async def handler(m):
            return m

        test_broker.include_router(router)

        async with test_broker:
            await test_broker.start()
            r = await test_broker.publish(
                "test",
                f"test/{queue}",
                callback=True,
            )

        assert r == "test"
