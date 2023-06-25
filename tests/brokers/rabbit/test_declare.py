import pytest

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from tests.tools.marks import needs_py38


@needs_py38
@pytest.mark.asyncio
async def test_declare_queue(
    broker: RabbitBroker, async_mock, mock, monkeypatch: pytest.MonkeyPatch, queue: str
):
    with monkeypatch.context():
        monkeypatch.setattr(broker, "_channel", mock)
        monkeypatch.setattr(broker.channel, "declare_queue", async_mock)

        q1 = await broker.declare_queue(RabbitQueue(queue))
        q2 = await broker.declare_queue(RabbitQueue(queue))

        with pytest.warns(DeprecationWarning):
            q3 = await broker._init_queue(RabbitQueue(queue))

    assert q1 is q2 is q3
    async_mock.assert_awaited_once()


@needs_py38
@pytest.mark.asyncio
async def test_declare_exchange(
    broker: RabbitBroker,
    async_mock,
    mock,
    monkeypatch: pytest.MonkeyPatch,
    queue: str,
):
    with monkeypatch.context():
        monkeypatch.setattr(broker, "_channel", mock)
        monkeypatch.setattr(broker.channel, "declare_exchange", async_mock)

        q1 = await broker.declare_exchange(RabbitExchange(queue))
        q2 = await broker.declare_exchange(RabbitExchange(queue))

        with pytest.warns(DeprecationWarning):
            q3 = await broker._init_exchange(RabbitExchange(queue))

    assert q1 is q2 is q3
    async_mock.assert_awaited_once()
