import pytest

from propan import RedisBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.redis
class TestRedisConnection(BrokerConnectionTestcase):
    broker = RedisBroker

    async def ping(self, broker: RedisBroker) -> bool:
        await broker._connection.ping()
        return True

    @pytest.mark.asyncio
    async def test_init_connect_by_raw_data(self, settings):
        async with RedisBroker(
            "redis://localhost:6378",  # will be ignored
            host=settings.host,
            port=settings.port,
        ) as broker:
            assert await self.ping(broker)

    @pytest.mark.asyncio
    async def test_connect_merge_kwargs_with_priority(self, settings):
        broker = RedisBroker(host="fake-host", port=6377)  # kwargs will be ignored
        assert await broker.connect(
            host=settings.host,
            port=settings.port,
        )
        await broker.close()
