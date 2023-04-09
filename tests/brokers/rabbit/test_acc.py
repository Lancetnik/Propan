from aio_pika import Message
import pytest

from propan.brokers.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from tests.tools.marks import needs_py38


@pytest.mark.asyncio
@pytest.mark.rabbit
@needs_py38
async def test_consume(
    async_mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    async with broker:
        broker.handle(queue)(async_mock)
        await broker.start()

        await broker.publish_message(message="hello", queue=queue)
        await wait_for_mock(async_mock)

    async_mock.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.rabbit
@needs_py38
async def test_consume_double(
    async_mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    async with broker:
        broker.handle(queue)(async_mock)
        await broker.start()

        await broker.publish_message("hello", queue=queue)
        await wait_for_mock(async_mock)

        await broker.publish_message("hello", queue=queue)
        await wait_for_mock(async_mock)

    assert async_mock.await_count == 2


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.rabbit
@needs_py38
async def test_different_consume(
    async_mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    another_queue = RabbitQueue(**queue.dict(exclude={"name"}), name=queue.name + "1")
    async with broker:
        broker.handle(queue)(async_mock.method)
        broker.handle(another_queue)(async_mock.method2)
        await broker.start()

        await broker.publish_message(message="hello", queue=queue)
        await broker.publish_message(message="hello", queue=another_queue)

        await wait_for_mock(async_mock.method)
        await wait_for_mock(async_mock.method2)

    async_mock.method.assert_awaited_once()
    async_mock.method2.assert_awaited_once()


@pytest.mark.asyncio
async def test_same_consume(queue: RabbitQueue, broker: RabbitBroker):
    broker.handle(queue)(lambda: None)
    with pytest.raises(ValueError):
        broker.handle(queue)(lambda: None)


@pytest.mark.asyncio
@pytest.mark.rabbit
@needs_py38
async def test_consume_from_exchange(
    async_mock,
    queue: RabbitQueue,
    exchange: RabbitExchange,
    broker: RabbitBroker,
    wait_for_mock,
):
    async with broker:
        broker.handle(queue=queue, exchange=exchange, retry=True)(async_mock)
        await broker.start()

        await broker.publish_message({"msg": "hello"}, queue=queue, exchange=exchange)

        await wait_for_mock(async_mock)

    async_mock.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.rabbit
@needs_py38
async def test_consume_with_get_old(
    async_mock,
    queue: RabbitQueue,
    exchange: RabbitExchange,
    broker: RabbitBroker,
    wait_for_mock,
):
    await broker.connect()
    await broker._init_channel()
    await broker._init_queue(queue)
    await broker._init_exchange(exchange)

    broker.handle(
        queue=RabbitQueue(name=queue.name, declare=False),
        exchange=RabbitExchange(name=exchange.name, declare=False),
        retry=1)(async_mock)
    await broker.start()

    await broker.publish_message(Message(b"hello"),
                                 queue=queue.name,
                                 exchange=exchange.name)

    await wait_for_mock(async_mock)

    async_mock.assert_awaited_once()
