import pytest

from propan import KafkaBroker


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_init_connect_by_url(settings):
    broker = KafkaBroker(settings.url)
    assert await broker.connect()
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_connection_by_url(settings):
    broker = KafkaBroker()
    assert await broker.connect(settings.url)
    await broker.close()
