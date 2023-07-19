import asyncio
from unittest.mock import Mock

from propan import RabbitBroker, RabbitRouter
from propan.brokers.rabbit import RabbitQueue
from propan.test.rabbit import build_message
from tests.brokers.base.router import RouterTestcase


class TestRabbitRouter(RouterTestcase):
    build_message = staticmethod(build_message)

    async def test_not_empty_prefix(
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

        @router.handle(r_queue)
        def subscriber(msg):
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
