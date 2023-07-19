import pytest

from propan import PropanApp
from propan.rabbit import RabbitBroker, TestRabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)


@broker.subscriber("test")
@broker.publisher("test-resp")
@broker.publisher("test-resp2")
async def handle():
    return "response"


@pytest.mark.asyncio
async def test_handle():
    async with TestRabbitBroker(broker) as br:
        await br.publish({"msg": "test"}, "test")

        # check an incoming message body
        handle.mock.assert_called_with({"msg": "test"})

        # check the publishers responses
        handle.response_mocks["default"]["test-resp"].assert_called_once_with("response")
        handle.response_mocks["default"]["test-resp2"].assert_called_once_with("response")
