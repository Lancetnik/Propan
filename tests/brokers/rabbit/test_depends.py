import aio_pika
import pytest
from propan.brokers.rabbit import RabbitBroker
from propan.utils.context import Depends, use_context


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_broker_depends(mock, queue, full_broker: RabbitBroker, wait_for_mock):
    @use_context
    def sync_depends(b, message):
        return message

    @use_context
    async def async_depends(b, message):
        return message

    check_message = None

    async def consumer(b, message, k1=Depends(sync_depends), k2=Depends(async_depends)):
        nonlocal check_message
        check_message = (
            isinstance(message, aio_pika.Message)
            and (message is k1)
            and (message is k2)
        )
        mock()

    mock.side_effect = consumer

    full_broker.handle(queue)(consumer)
    await full_broker.start()

    await full_broker.publish_message(message={"msg": "hello"}, queue=queue)
    await wait_for_mock(mock)

    assert check_message is True


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.rabbit
async def test_different_consumers_has_different_messages(
    mock, context, wait_for_mock, full_broker: RabbitBroker
):
    message1 = None

    async def consumer1(b, message):
        nonlocal message1
        mock.first()
        message1 = message

    message2 = None

    async def consumer2(b, message):
        nonlocal message2
        mock.second()
        message2 = message

    full_broker.handle("test_different_consume_1")(consumer1)
    full_broker.handle("test_different_consume_2")(consumer2)

    await full_broker.start()

    await full_broker.publish_message(
        message="hello1", queue="test_different_consume_1"
    )
    await full_broker.publish_message(
        message="hello2", queue="test_different_consume_2"
    )

    await wait_for_mock(mock.first)
    await wait_for_mock(mock.second)

    assert isinstance(message1, aio_pika.Message)
    assert isinstance(message2, aio_pika.Message)
    assert message1 != message2
    assert context.message is None
