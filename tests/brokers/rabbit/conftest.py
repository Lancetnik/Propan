from dataclasses import dataclass

import pytest
import pytest_asyncio

from propan.rabbit import RabbitBroker, RabbitExchange, RabbitRouter, TestRabbitBroker


@dataclass
class Settings:
    url = "amqp://guest:guest@localhost:5672/"

    host = "localhost"
    port = 5672
    login = "guest"
    password = "guest"

    queue = "test_queue"


@pytest.fixture
def exchange(queue):
    return RabbitExchange(name=queue)


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.fixture
def router():
    return RabbitRouter()


@pytest_asyncio.fixture
@pytest.mark.rabbit
async def broker(settings):
    broker = RabbitBroker(settings.url, apply_types=False)
    async with broker:
        yield broker


@pytest_asyncio.fixture
@pytest.mark.rabbit
async def full_broker(settings):
    broker = RabbitBroker(settings.url)
    async with broker:
        yield broker


@pytest_asyncio.fixture
async def test_broker():
    broker = RabbitBroker()
    async with TestRabbitBroker(broker) as br:
        yield br
