import pytest

from propan import RedisBroker


@pytest.mark.asyncio
@pytest.mark.redis
async def test_init_connect_by_url(broker):
    assert await broker.connect()
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connect_by_url(settings):
    broker = RedisBroker()
    assert await broker.connect(settings.url)
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connect_by_url_priority(settings):
    broker = RedisBroker("wrong_url")
    assert await broker.connect(settings.url)
    await broker.close()
