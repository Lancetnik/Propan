import pytest
import pytest_asyncio
from aiobotocore.config import AioConfig
from botocore import UNSIGNED
from pydantic import BaseSettings

from propan import SQSBroker
from propan.test import TestSQSBroker


class Settings(BaseSettings):
    url = "http://localhost:9324/"
    region_name = "us-west-2"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.redis
async def broker(settings: Settings):
    broker = SQSBroker(
        settings.url,
        region_name=settings.region_name,
        config=AioConfig(signature_version=UNSIGNED),
        apply_types=False,
    )
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = SQSBroker()
    yield TestSQSBroker(broker)
