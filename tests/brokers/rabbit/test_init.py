import pytest

from propan.brokers.rabbit import RabbitBroker


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_set_max():
    broker = RabbitBroker(logger=None, consumers=10)
    await broker.start()
    assert broker._channel._prefetch_count == 10
    await broker.close()
