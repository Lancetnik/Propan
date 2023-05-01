from asyncio import Event, wait_for

import pytest
from aio_pika import Message

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume(
    mock,
    queue: RabbitQueue,
    broker: RabbitBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(queue, retry=1)(mock)
        await broker.start()
        await broker.publish(message="hello", queue=queue)
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume_double(
    mock,
    queue: RabbitQueue,
    broker: RabbitBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(queue)(mock)
        await broker.start()

        await broker.publish("hello", queue=queue)
        await wait_for(consume.wait(), 3)

        consume.clear()
        await broker.publish("hello", queue=queue)
        await wait_for(consume.wait(), 3)

    assert mock.call_count == 2


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_different_consume(
    mock,
    queue: RabbitQueue,
    broker: RabbitBroker,
):
    first_consume = Event()
    second_consume = Event()

    mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
    mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

    another_queue = RabbitQueue(**queue.dict(exclude={"name"}), name=queue.name + "1")
    async with broker:
        broker.handle(queue)(mock.method)
        broker.handle(another_queue)(mock.method2)
        await broker.start()

        await broker.publish(message="hello", queue=queue)
        await broker.publish(message="hello", queue=another_queue)

        await wait_for(first_consume.wait(), 3)
        await wait_for(second_consume.wait(), 3)

    mock.method.assert_called_once()
    mock.method2.assert_called_once()


@pytest.mark.asyncio
async def test_same_consume(
    queue: RabbitQueue,
    broker: RabbitBroker,
):
    broker.handle(queue)(lambda: None)
    with pytest.raises(ValueError):
        broker.handle(queue)(lambda: None)


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume_from_exchange(
    mock,
    queue: RabbitQueue,
    exchange: RabbitExchange,
    broker: RabbitBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    async with broker:
        broker.handle(queue=queue, exchange=exchange, retry=True)(mock)
        await broker.start()
        await broker.publish({"msg": "hello"}, queue=queue, exchange=exchange)
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume_with_get_old(
    mock,
    queue: RabbitQueue,
    exchange: RabbitExchange,
    broker: RabbitBroker,
):
    consume = Event()
    mock.side_effect = lambda *_: consume.set()  # pragma: no branch

    await broker.connect()
    await broker._init_channel()
    await broker._init_queue(queue)
    await broker._init_exchange(exchange)

    broker.handle(
        queue=RabbitQueue(name=queue.name, passive=True),
        exchange=RabbitExchange(name=exchange.name, passive=True),
    )(mock)

    async with broker:
        await broker.start()
        await broker.publish(
            Message(b"hello"), queue=queue.name, exchange=exchange.name
        )
        await wait_for(consume.wait(), 3)

    mock.assert_called_once()
