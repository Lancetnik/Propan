import pytest
from propan.brokers.rabbit import RabbitBroker


@pytest.mark.asyncio
async def test_set_max():
    broker = RabbitBroker(logger=None, consumers=10)
    await broker.start()
    assert broker._channel._prefetch_count == 10
    await broker.close()


@pytest.mark.asyncio
async def test_set_max_by_method():
    broker = RabbitBroker(logger=None, consumers=10)
    await broker.connect()
    await broker._init_channel(20)
    await broker.start()
    assert broker._channel._prefetch_count == 20
    await broker.close()


@pytest.mark.asyncio
async def test_init_vefore_started():
    broker = RabbitBroker()
    with pytest.raises(ValueError):
        await broker._init_channel()
