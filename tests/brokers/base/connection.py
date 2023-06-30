from typing import Type

import pytest

from propan.brokers._model import BrokerAsyncUsecase


class BrokerConnectionTestcase:
    broker: Type[BrokerAsyncUsecase]

    def get_broker_args(self, settings):
        return (settings.url,), {}

    async def ping(self, broker) -> bool:
        return True

    @pytest.mark.asyncio
    async def test_warning(self, broker: BrokerAsyncUsecase):
        async with broker:
            await broker.start()
            assert broker.started
            with pytest.warns(RuntimeWarning):
                broker.handle("test")
        assert not broker.started

    @pytest.mark.asyncio
    async def test_init_connect_by_url(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker(*args, **kwargs)
        assert await broker.connect()
        assert await self.ping(broker)
        await broker.close()

    @pytest.mark.asyncio
    async def test_connection_by_url(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker()
        assert await broker.connect(*args, **kwargs)
        assert await self.ping(broker)
        await broker.close()

    @pytest.mark.asyncio
    async def test_connect_by_url_priority(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker("wrong_url")
        assert await broker.connect(*args, **kwargs)
        assert await self.ping(broker)
        await broker.close()

    @pytest.mark.asyncio
    async def test_connect_merge_args_and_kwargs_base(self, settings):
        args, kwargs = self.get_broker_args(settings)
        broker = self.broker(*args)
        assert await broker.connect(**kwargs)
        assert await self.ping(broker)
        await broker.close()
