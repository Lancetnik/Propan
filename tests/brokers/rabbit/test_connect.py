import pytest
from propan import RabbitBroker


async def _init_channel(broker):
    await broker._init_channel()
    try:
        return True
    finally:
        await broker.close()


async def _connect(broker):
    await broker.connect()
    return await _init_channel(broker)


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_init_connect_by_url(settings):
    broker = RabbitBroker(url=settings.url)
    assert await _connect(broker)


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_init_connect_by_raw_data(settings):
    broker = RabbitBroker(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port,
    )
    assert await _connect(broker)


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connection_by_url(settings):
    broker = RabbitBroker()
    await broker.connect(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port,
    )
    assert await _init_channel(broker)


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_connection_params(settings):
    broker = RabbitBroker()
    await broker.connect(settings.url)
    assert await _init_channel(broker)
