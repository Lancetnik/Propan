from asyncio import Event, wait_for

import pytest

from propan import RedisBroker


@pytest.mark.asyncio
@pytest.mark.redis
async def test_consume(
    mock,
    channel_name: str,
    broker: RedisBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(channel_name)(mock)
        await broker.start()
        await broker.publish("hello", channel_name)
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.redis
async def test_pattern_consume(
    mock,
    channel_name: str,
    broker: RedisBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle("*", pattern=True)(mock)
        await broker.start()
        await broker.publish("hello", channel_name)
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.redis
async def test_consume_from_native_redis(
    mock,
    channel_name: str,
    broker: RedisBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(channel_name)(mock)
        await broker.start()
        await broker._connection.publish(channel_name, "msg")
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.redis
async def test_consume_double(
    mock,
    channel_name: str,
    broker: RedisBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(channel_name)(mock)
        await broker.start()

        await broker.publish("hello", channel_name)
        await wait_for(consume.wait(), 3)

        consume.clear()
        await broker.publish("hello", channel_name)
        await wait_for(consume.wait(), 3)

    assert mock.call_count == 2


@pytest.mark.asyncio
@pytest.mark.redis
async def test_different_consume(
    mock,
    channel_name: str,
    broker: RedisBroker,
):
    first_consume = Event()
    second_consume = Event()

    mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
    mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

    another_channel = channel_name + "1"
    async with broker:
        broker.handle(channel_name)(mock.method)
        broker.handle(another_channel)(mock.method2)
        await broker.start()

        await broker.publish("hello", channel_name)
        await broker.publish("hello", another_channel)

        await wait_for(first_consume.wait(), 3)
        await wait_for(second_consume.wait(), 3)

    mock.method.assert_called_once()
    mock.method2.assert_called_once()
