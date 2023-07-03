import pytest
from nats.js.client import JetStreamContext

from propan import NatsJSBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.nats
class TestNatsJSConnect(BrokerConnectionTestcase):
    broker = NatsJSBroker

    @pytest.mark.asyncio
    async def test_connect_merge_args_and_kwargs_native(self, settings):
        broker = self.broker("fake-url")  # will be ignored
        assert await broker.connect(servers=settings.url)
        await broker.close()

    @pytest.mark.asyncio
    async def test_js_exists(self, settings):
        broker = self.broker(settings.url)
        assert await broker.connect()
        assert isinstance(broker.js, JetStreamContext)
        await broker.close()
