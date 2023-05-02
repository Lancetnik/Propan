import aio_pika
import pytest

from propan.annotations import RabbitMessage
from propan.brokers.rabbit import RabbitBroker
from propan.utils import Depends


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_broker_depends(
    queue,
    full_broker: RabbitBroker,
):
    def sync_depends(message: RabbitMessage):
        return message

    async def async_depends(message: RabbitMessage):
        return message

    check_message = None

    async def consumer(
        message: RabbitMessage,
        k1=Depends(sync_depends),
        k2=Depends(async_depends),
    ):
        nonlocal check_message
        check_message = (
            isinstance(message, aio_pika.Message)
            and (message is k1)
            and (message is k2)
        )

    full_broker.handle(queue)(consumer)
    await full_broker.start()

    await full_broker.publish(queue=queue, callback=True)
    assert check_message is True


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_different_consumers_has_different_messages(
    context,
    full_broker: RabbitBroker,
):
    message1 = None

    async def consumer1(message: RabbitMessage):
        nonlocal message1
        message1 = message

    message2 = None

    async def consumer2(message: RabbitMessage):
        nonlocal message2
        message2 = message

    full_broker.handle("test_different_consume_1")(consumer1)
    full_broker.handle("test_different_consume_2")(consumer2)

    await full_broker.start()

    await full_broker.publish(queue="test_different_consume_1", callback=True)
    await full_broker.publish(queue="test_different_consume_2", callback=True)

    assert isinstance(message1, aio_pika.Message)
    assert isinstance(message2, aio_pika.Message)
    assert message1 != message2
    assert context.message is None
