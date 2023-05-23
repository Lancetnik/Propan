from asyncio import Event, wait_for

import pytest

from propan import KafkaBroker


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_consume(
    mock,
    topic: str,
    broker: KafkaBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(topic)(mock)
        await broker.start()
        await broker.publish("hello", topic)
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_consume_double(
    mock,
    topic: str,
    broker: KafkaBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(topic)(mock)
        await broker.start()

        await broker.publish("hello", topic)
        await wait_for(consume.wait(), 3)

        consume.clear()
        await broker.publish("hello", topic)
        await wait_for(consume.wait(), 3)

    assert mock.call_count == 2


@pytest.mark.asyncio
@pytest.mark.kafka
async def test_different_consume(
    mock,
    topic: str,
    broker: KafkaBroker,
):
    first_consume = Event()
    second_consume = Event()

    mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
    mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

    another_topic = topic + "1"
    async with broker:
        broker.handle(topic)(mock.method)
        broker.handle(another_topic)(mock.method2)
        await broker.start()

        await broker.publish("hello", topic)
        await broker.publish("hello", another_topic)

        await wait_for(first_consume.wait(), 3)
        await wait_for(second_consume.wait(), 3)

    mock.method.assert_called_once()
    mock.method2.assert_called_once()
