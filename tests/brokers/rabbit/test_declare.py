import pytest

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from tests.tools.marks import needs_py38


@needs_py38
@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_declare_queue(
    broker: RabbitBroker, async_mock, monkeypatch: pytest.MonkeyPatch, queue: str
):
    async with broker:
        with monkeypatch.context():
            monkeypatch.setattr(broker.channel, "declare_queue", async_mock)

            q1 = await broker.declare_queue(RabbitQueue(queue))
            q2 = await broker.declare_queue(RabbitQueue(queue))

    assert q1 is q2
    async_mock.assert_awaited_once()


@needs_py38
@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_declare_exchange(
    broker: RabbitBroker,
    async_mock,
    monkeypatch: pytest.MonkeyPatch,
    exchange: RabbitExchange,
):
    async with broker:
        with monkeypatch.context():
            monkeypatch.setattr(broker.channel, "declare_exchange", async_mock)

            q1 = await broker.declare_exchange(exchange)
            q2 = await broker.declare_exchange(exchange.copy())

    assert q1 is q2
    async_mock.assert_awaited_once()
