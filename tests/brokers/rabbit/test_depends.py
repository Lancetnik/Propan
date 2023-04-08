import pytest
from propan.brokers.rabbit import RabbitBroker
from propan.utils.context import Depends, use_context


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_broker_depends(mock, queue, broker: RabbitBroker, wait_for_mock):
    @use_context
    def sync_depends(b, message):
        return message

    @use_context
    async def async_depends(b, message):
        return message

    async with broker:
        check_message = None

        async def consumer(
            message, k1=Depends(sync_depends), k2=Depends(async_depends)
        ):
            nonlocal check_message
            check_message = message is k1 is k2
            mock()

        mock.side_effect = consumer

        broker.handle(queue)(consumer)

        await broker.start()

        await broker.publish_message(message="hello", queue=queue)

        await wait_for_mock(mock)

    assert check_message is True


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.rabbit
async def test_different_consumers_has_different_messages(
    mock, context, wait_for_mock, broker: RabbitBroker
):
    message1 = None

    async def consumer1(message):
        nonlocal message1
        mock.first()
        message1 = message

    message2 = None

    async def consumer2(message):
        nonlocal message2
        mock.second()
        message2 = message

    async with broker:
        broker.handle("test_different_consume_1")(consumer1)

        broker.handle("test_different_consume_2")(consumer2)

        await broker.start()

        await broker.publish_message(message="hello1", queue="test_different_consume_1")
        await broker.publish_message(message="hello2", queue="test_different_consume_2")

        await wait_for_mock(mock.first)
        await wait_for_mock(mock.second)

    assert message1 is not None
    assert message2 is not None
    assert message1 != message2
    assert context.context["message"] is None
