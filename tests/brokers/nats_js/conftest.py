from dataclasses import dataclass

import pytest
import pytest_asyncio

from propan import NatsJSBroker, NatsRouter
from propan.test import TestNatsBroker


@dataclass
class Settings:
    url = "nats://localhost:4222"


@pytest.fixture()
def router():
    return NatsRouter()


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.mark.nats
@pytest_asyncio.fixture()
async def broker(settings):
    broker = NatsJSBroker(
        settings.url,
        apply_types=False,
    )
    yield broker
    await broker.close()


@pytest.mark.nats
@pytest_asyncio.fixture()
async def full_broker(settings):
    broker = NatsJSBroker(settings.url)
    yield broker
    await broker.close()


@pytest.fixture()
def test_broker():
    broker = NatsJSBroker()
    yield TestNatsBroker(broker)
