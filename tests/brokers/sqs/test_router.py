import asyncio
from unittest.mock import Mock

from propan import SQSBroker, SQSRouter
from propan.test.sqs import build_message
from propan.brokers.sqs.schema import SQSQueue

from tests.brokers.base.router import RouterTestcase


class TestSQSRouter(RouterTestcase):
    build_message = staticmethod(build_message)

    async def test_not_empty_prefix(
        self,
        mock: Mock,
        router: SQSRouter,
        broker: SQSBroker,
        queue: str,
    ):
        router.prefix = "test_"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        r_queue = SQSQueue(queue)

        @router.handle(r_queue)
        def subscriber(msg):
            mock()

        broker.include_router(router)

        await broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(broker.publish("hello", f"test_{r_queue.name}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()
