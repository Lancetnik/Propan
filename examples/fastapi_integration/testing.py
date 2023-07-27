import pytest
import pytest_asyncio
from propan.rabbit.test import TestRabbitBroker
from fastapi.exceptions import RequestValidationError

from .app import router, publisher, handler


@pytest_asyncio.fixture
async def broker():
    async with TestRabbitBroker(router.broker) as br:
        yield br


@pytest.mark.asyncio
async def test_incorrect(broker):
    with pytest.raises(RequestValidationError):
        await broker.publish("user-id", "test-q")


@pytest.mark.asyncio
async def test_handler(broker):
    user_id = 1

    await broker.publish(user_id, "test-q")

    handler.mock.assert_called_once_with(user_id)
    publisher.mock.assert_called_once_with(f"{user_id} created")
