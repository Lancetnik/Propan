import aio_pika
import pytest

from propan.rabbit import RabbitBroker
from propan.rabbit.annotations import RabbitMessage
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

    @full_broker.subscriber(queue)
    async def h(
        message: RabbitMessage,
        k1=Depends(sync_depends),
        k2=Depends(async_depends),
    ):
        nonlocal check_message
        check_message = (
            isinstance(message.raw_message, aio_pika.IncomingMessage)
            and (message is k1)
            and (message is k2)
        )

    await full_broker.start()

    await full_broker.publish(queue=queue, rpc=True)
    assert check_message is True


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_different_consumers_has_different_messages(
    context,
    full_broker: RabbitBroker,
):
    message1 = None

    @full_broker.subscriber("test_different_consume_1")
    async def consumer1(message: RabbitMessage):
        nonlocal message1
        message1 = message

    message2 = None

    @full_broker.subscriber("test_different_consume_2")
    async def consumer2(message: RabbitMessage):
        nonlocal message2
        message2 = message

    await full_broker.start()

    await full_broker.publish(queue="test_different_consume_1", rpc=True)
    await full_broker.publish(queue="test_different_consume_2", rpc=True)

    assert isinstance(message1.raw_message, aio_pika.IncomingMessage)
    assert isinstance(message2.raw_message, aio_pika.IncomingMessage)
    assert message1 != message2
    assert context.message is None
