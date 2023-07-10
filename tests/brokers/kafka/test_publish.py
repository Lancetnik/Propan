import asyncio

import pytest

from propan import KafkaBroker
from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.kafka
@pytest.mark.slow
class TestKafkaPublish(BrokerPublishTestcase):
    @pytest.mark.asyncio
    async def test_publish_batch(self, queue: str, broker: KafkaBroker):
        msgs_queue = asyncio.Queue(maxsize=2)

        @broker.handle(queue)
        async def handler(msg):
            await msgs_queue.put(msg)

        async with broker:
            await broker.start()

            await broker.publish_batch(1, "hi", topic=queue)

            result, _ = await asyncio.wait(
                (
                    asyncio.create_task(msgs_queue.get()),
                    asyncio.create_task(msgs_queue.get()),
                ),
                timeout=3,
            )

        assert {1, "hi"} == {r.result() for r in result}
