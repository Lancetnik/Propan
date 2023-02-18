import pytest

from propan.brokers import RabbitBroker, ConnectionData


async def _init_channel(broker):
    await broker.init_channel()
    try:
        return True
    finally:
        await broker.close()


async def _connect(broker):
    await broker.connect()
    return await _init_channel(broker)


@pytest.mark.asyncio
async def test_init_connect_by_url(settings):
    broker = RabbitBroker(url=settings.url)
    assert await _connect(broker)


@pytest.mark.asyncio
async def test_init_connect_by_connection_data(settings):
    connection = ConnectionData(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port
    )
    broker = RabbitBroker(connection_data=connection)
    assert await _connect(broker)


@pytest.mark.asyncio
async def test_init_connect_by_raw_data(settings):
    broker = RabbitBroker(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port
    )
    assert await _connect(broker)


@pytest.mark.asyncio
async def test_connection_by_url(settings):
    broker = RabbitBroker()
    await broker.connect(
        host=settings.host,
        login=settings.login,
        password=settings.password,
        port=settings.port
    )
    assert await _init_channel(broker)


@pytest.mark.asyncio
async def test_connection_params(settings):
    broker = RabbitBroker()
    await broker.connect(settings.url)
    assert await _init_channel(broker)
