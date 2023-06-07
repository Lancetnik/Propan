import pytest
from aiobotocore.config import AioConfig
from botocore import UNSIGNED

from propan import SQSBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.sqs
class TestSQSConnection(BrokerConnectionTestcase):
    broker = SQSBroker

    def get_broker_args(self, settings):
        return (settings.url,), {
            "region_name": settings.region_name,
            "config": AioConfig(signature_version=UNSIGNED),
        }

    @pytest.mark.asyncio
    async def test_connect_merge_args_and_kwargs_native(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker("fake-url")  # will be ignored
        assert await broker.connect(url=settings.url, **kwargs)
        await broker.close()
