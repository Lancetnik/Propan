from uuid import uuid4

import pytest
import pytest_asyncio
from propan.brokers.rabbit import RabbitBroker, RabbitQueue
from pydantic import BaseSettings


class Settings(BaseSettings):
    url = "amqp://guest:guest@localhost:5672/"

    host = "localhost"
    port = 5672
    login = "guest"
    password = "guest"

    queue = "test_queue"


@pytest.fixture
def queue():
    name = str(uuid4())
    return RabbitQueue(name=name, declare=True)


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.rabbit
async def broker(settings):
    broker = RabbitBroker(settings.url)
    yield broker
    await broker.close()
