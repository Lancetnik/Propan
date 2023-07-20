import asyncio
from unittest.mock import Mock

import pytest

from propan.rabbit import RabbitBroker, RabbitQueue, RabbitRouter
from tests.brokers.base.router import RouterLocalTestcase, RouterTestcase


@pytest.mark.rabbit
class TestRabbitRouter(RouterTestcase):
    async def test_queue_obj(
        self,
        mock: Mock,
        router: RabbitRouter,
        broker: RabbitBroker,
        queue: str,
    ):
        router.prefix = "test/"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        r_queue = RabbitQueue(queue)

        @router.subscriber(r_queue)
        def subscriber():
            mock()

        broker.include_router(router)

        await broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(broker.publish("hello", f"test/{r_queue.name}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()


class TestRabbitRouterLocal(RouterLocalTestcase):
    pass
