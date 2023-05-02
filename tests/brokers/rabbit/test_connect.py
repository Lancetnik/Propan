import pytest

from propan.brokers.rabbit import RabbitBroker


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_init_connect_by_url(settings):
    broker = RabbitBroker(url=settings.url)
    assert await broker.connect()
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_init_connect_by_raw_data(settings):
    broker = RabbitBroker(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port,
    )
    assert await broker.connect()
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connection_by_url(settings):
    broker = RabbitBroker()
    assert await broker.connect(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port,
    )
    await broker.close()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connection_params(settings):
    broker = RabbitBroker()
    assert await broker.connect(settings.url)
    await broker.close()
