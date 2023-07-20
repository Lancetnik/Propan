from dataclasses import dataclass

import pytest
import pytest_asyncio

from propan import MqttBroker


@dataclass
class Settings:
    url = "localhost"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.mqtt
async def broker(settings):
    broker = MqttBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()


@pytest_asyncio.fixture
@pytest.mark.mqtt
async def full_broker(settings):
    broker = MqttBroker(settings.url)
    yield broker
    await broker.close()
