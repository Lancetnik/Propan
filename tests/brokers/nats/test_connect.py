import pytest

from propan import NatsBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.nats
class TestNatsConnect(BrokerConnectionTestcase):
    broker = NatsBroker

    @pytest.mark.asyncio
    async def test_connect_merge_args_and_kwargs(self, settings):
        broker = self.broker("fake-url")  # will be ignored
        assert await broker.connect(servers=settings.url)
        await broker.close()
