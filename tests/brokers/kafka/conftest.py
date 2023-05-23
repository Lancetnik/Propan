from uuid import uuid4

import pytest
import pytest_asyncio
from pydantic import BaseSettings

from propan import KafkaBroker
from propan.test.kafka import TestKafkaBroker


class Settings(BaseSettings):
    url = "localhost:9092"


@pytest.fixture
def topic():
    return str(uuid4())


@pytest.fixture
def exchange():
    name = str(uuid4())
    return name


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.kafka
async def broker(settings):
    broker = KafkaBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
@pytest.mark.kafka
async def full_broker(settings):
    broker = KafkaBroker(settings.url)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = KafkaBroker()
    yield TestKafkaBroker(broker)
