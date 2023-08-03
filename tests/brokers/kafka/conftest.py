from dataclasses import dataclass

import pytest
import pytest_asyncio

from propan.kafka import KafkaBroker, KafkaRouter


@dataclass
class Settings:
    url = "localhost:9092"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.fixture
def router():
    return KafkaRouter()


@pytest_asyncio.fixture
@pytest.mark.kafka
async def broker(settings):
    broker = KafkaBroker(settings.url, apply_types=False)
    async with broker:
        yield broker


@pytest_asyncio.fixture
@pytest.mark.kafka
async def full_broker(settings):
    broker = KafkaBroker(settings.url)
    async with broker:
        yield broker
