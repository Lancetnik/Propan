from typing import Type

import pytest

from propan.brokers.model import BrokerUsecase


class BrokerConnectionTestcase:
    broker: Type[BrokerUsecase]

    @pytest.mark.asyncio
    async def test_init_connect_by_url(self, settings):
        broker = self.broker(settings.url)
        assert await broker.connect()
        await broker.close()

    @pytest.mark.asyncio
    async def test_connection_by_url(self, settings):
        broker = self.broker()
        assert await broker.connect(settings.url)
        await broker.close()

    @pytest.mark.asyncio
    async def test_connect_by_url_priority(self, settings):
        broker = self.broker("wrong_url")
        assert await broker.connect(settings.url)
        await broker.close()
