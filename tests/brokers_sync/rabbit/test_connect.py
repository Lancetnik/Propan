import pytest

from propan import RabbitSyncBroker
from tests.brokers_sync.base.connection import BrokerConnectionTestcase


@pytest.mark.rabbit
class TestRabbitConnection(BrokerConnectionTestcase):
    broker = RabbitSyncBroker

    def test_init_connect_by_raw_data(self, settings):
        broker = self.broker(
            url=settings.url,
            login=settings.login,
            password=settings.password,
            port=settings.port,
        )
        assert broker.connect()
        broker.close()

    def test_connection_by_params(self, settings):
        broker = self.broker()
        assert broker.connect(
            url=settings.url,
            login=settings.login,
            password=settings.password,
            port=settings.port,
        )
        broker.close()

    def test_connect_merge_kwargs_with_priority(self, settings):
        broker = self.broker(url="fake-host", port=5677)  # kwargs will be ignored
        assert broker.connect(
            url=settings.url,
            login=settings.login,
            password=settings.password,
            port=settings.port,
        )
        broker.close()

    def test_connect_merge_args_and_kwargs_native(self, settings):
        broker = self.broker("fake-url")  # will be ignored
        assert broker.connect(url=settings.url)
        broker.close()
