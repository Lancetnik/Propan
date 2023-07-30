import pytest

from propan import PropanApp
from propan.rabbit import RabbitBroker, TestRabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)


@broker.subscriber("test-queue")
async def handle(msg):
    raise ValueError()


@pytest.mark.asyncio
async def test_handle():
    async with TestRabbitBroker(broker) as br:
        with pytest.raises(ValueError):
            await br.publish("hello!", "test-queue")
