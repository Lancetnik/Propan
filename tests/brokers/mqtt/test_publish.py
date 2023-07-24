import asyncio

import pytest

from propan import MqttBroker
from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.mqtt
@pytest.mark.slow
class TestMqttPublish(BrokerPublishTestcase):
    @pytest.mark.asyncio
    async def test_publish(self, topic: str, broker: MqttBroker):
        msgs_queue = asyncio.Queue(maxsize=2)

        @broker.handle(topic)
        async def handler(msg):
            await msgs_queue.put(msg.body)

        async with broker:
            await broker.start()

            await broker.publish({"body", "hi"}, topic=topic)
            await broker.publish({"body", 1}, topic=topic)

            result, _ = await asyncio.wait(
                (
                    asyncio.create_task(msgs_queue.get()),
                    asyncio.create_task(msgs_queue.get()),
                ),
                timeout=3,
            )

        assert {1, "hi"} == {r.result() for r in result}
