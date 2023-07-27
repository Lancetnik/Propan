import asyncio

import pytest

from propan.rabbit import RabbitBroker, RabbitQueue, RabbitRouter
from tests.brokers.base.router import RouterLocalTestcase, RouterTestcase


@pytest.mark.rabbit
class TestRouter(RouterTestcase):
    broker_class = RabbitRouter

    async def test_queue_obj(
        self,
        router: RabbitRouter,
        broker: RabbitBroker,
        queue: str,
        event: asyncio.Event,
    ):
        router.prefix = "test/"

        r_queue = RabbitQueue(queue)

        @router.subscriber(r_queue)
        def subscriber(m):
            event.set()

        broker.include_router(router)

        await broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(broker.publish("hello", f"test/{r_queue.name}")),
                asyncio.create_task(event.wait()),
            ),
            timeout=3,
        )

        assert event.is_set()


class TestRabbitRouterLocal(RouterLocalTestcase):
    broker_class = RabbitRouter
