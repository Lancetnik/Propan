import pytest

from propan import RedisBroker
from propan.test.redis import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestKafkaTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)

    @pytest.mark.asyncio
    async def test_pattern_consume(self, queue: str, test_broker: RedisBroker):
        @test_broker.handle(".*", pattern=True)
        async def m():  # pragma: no cover
            return 1

        async with test_broker:
            await test_broker.start()

            assert (
                await test_broker.publish(
                    message="hello",
                    channel=queue,
                    callback=True,
                )
            ) == 1
