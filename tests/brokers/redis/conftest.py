from dataclasses import dataclass

import pytest
import pytest_asyncio

from propan import RedisBroker, RedisRouter
from propan.test import TestRedisBroker


@dataclass
class Settings:
    url = "redis://localhost:6379"

    host = "localhost"
    port = 6379


@pytest.fixture()
def router():
    return RedisRouter()


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.redis
async def broker(settings):
    broker = RedisBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
@pytest.mark.redis
async def full_broker(settings):
    broker = RedisBroker(settings.url)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = RedisBroker()
    yield TestRedisBroker(broker)
