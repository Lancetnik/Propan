from typing import Type

import pytest

from propan.brokers._model import BrokerSyncUsecase


class BrokerConnectionTestcase:
    broker: BrokerSyncUsecase

    def get_broker_args(self, settings):
        return (settings.url,), {}

    def ping(self, broker) -> bool:
        return True

    def test_warning(self, broker: BrokerSyncUsecase):
        with broker:
            broker.start()
            assert broker.started
            with pytest.warns(RuntimeWarning):
                broker.handle("test")
        assert not broker.started


    def test_init_connect_by_url(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker(*args, **kwargs)
        assert broker.connect()
        assert self.ping(broker)
        broker.close()

    def test_connection_by_url(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker()
        assert broker.connect(*args, **kwargs)
        assert self.ping(broker)
        broker.close()

    def test_connect_by_url_priority(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker("wrong_url")
        assert broker.connect(*args, **kwargs)
        assert self.ping(broker)
        broker.close()

    def test_connect_merge_args_and_kwargs_base(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker(*args)
        assert broker.connect(**kwargs)
        assert self.ping(broker)
        broker.close()
