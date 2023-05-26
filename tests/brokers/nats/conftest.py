import pytest
import pytest_asyncio
from pydantic import BaseSettings

from propan import NatsBroker
from propan.test import TestNatsBroker


class Settings(BaseSettings):
    url = "nats://localhost:4222"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.nats
async def broker(settings):
    broker = NatsBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
@pytest.mark.nats
async def full_broker(settings):
    broker = NatsBroker(settings.url)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = NatsBroker()
    yield TestNatsBroker(broker)
