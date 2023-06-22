from dataclasses import dataclass
from uuid import uuid4

import pytest
import pytest_asyncio

from propan.brokers.rabbit import RabbitBroker, RabbitExchange
from propan.test import TestRabbitBroker


@dataclass
class Settings:
    url = "amqp://guest:guest@localhost:5672/"

    host = "localhost"
    port = 5672
    login = "guest"
    password = "guest"

    queue = "test_queue"


@pytest.fixture
def queue():
    name = str(uuid4())
    return name


@pytest.fixture
def exchange():
    name = str(uuid4())
    return RabbitExchange(name=name)


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.rabbit
async def broker(settings):
    broker = RabbitBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
@pytest.mark.rabbit
async def full_broker(settings):
    broker = RabbitBroker(settings.url)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = RabbitBroker()
    yield TestRabbitBroker(broker)
    await broker.close()
