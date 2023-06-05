import pytest

from propan import KafkaBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.kafka
class TestKafkaConnect(BrokerConnectionTestcase):
    broker = KafkaBroker

    @pytest.mark.asyncio
    async def test_connect_merge_args_and_kwargs(self, settings):
        broker = self.broker("fake-url")  # will be ignored
        assert await broker.connect(bootstrap_servers=settings.url)
        await broker.close()
