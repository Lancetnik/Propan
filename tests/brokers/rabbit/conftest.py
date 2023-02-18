import pytest
import pytest_asyncio
from pydantic import BaseSettings

from propan.brokers import RabbitBroker


class Settings(BaseSettings):
    url = "amqp://user:password@localhost:5672/"

    host = "localhost"
    port = 5672
    login = "user"
    password = "password"

    queue = "test_queue"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
async def broker(settings):
    broker = RabbitBroker(settings.url)
    await broker.connect()
    await broker.init_channel()
    yield broker
    await broker.close()
