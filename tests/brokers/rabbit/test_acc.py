from unittest.mock import Mock

import pytest
from propan.brokers.rabbit import RabbitBroker, RabbitQueue


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume(
    mock: Mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    async with broker:
        broker.handle(queue)(mock.method)
        await broker.start()

        await broker.publish_message(message="hello", queue=queue)
        await wait_for_mock(mock.method)

    mock.method.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_consume_double(
    mock: Mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    async with broker:
        broker.handle(queue)(mock.method)
        await broker.start()

        await broker.publish_message("hello", queue=queue)
        await wait_for_mock(mock.method)

        await broker.publish_message("hello", queue=queue)
        await wait_for_mock(mock.method)

    assert mock.method.call_count == 2


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.rabbit
async def test_different_consume(
    mock: Mock, queue: RabbitQueue, broker: RabbitBroker, wait_for_mock
):
    another_queue = RabbitQueue(**queue.dict(exclude={"name"}), name=queue.name + "1")
    async with broker:
        broker.handle(queue)(mock.method)
        broker.handle(another_queue)(mock.method2)
        await broker.start()

        await broker.publish_message(message="hello", queue=queue)
        await broker.publish_message(message="hello", queue=another_queue)

        await wait_for_mock(mock.method)
        await wait_for_mock(mock.method2)

    mock.method.assert_called_once()
    mock.method2.assert_called_once()


@pytest.mark.asyncio
async def test_same_consume(queue: RabbitQueue, broker: RabbitBroker):
    broker.handle(queue)(lambda: None)
    with pytest.raises(ValueError):
        broker.handle(queue)(lambda: None)
