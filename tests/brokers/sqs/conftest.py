from dataclasses import dataclass
from uuid import uuid4

import pytest
import pytest_asyncio
from aiobotocore.config import AioConfig
from botocore import UNSIGNED

from propan import SQSBroker
from propan.test import TestSQSBroker


@dataclass
class Settings:
    url = "http://localhost:9324/"
    region_name = "us-west-2"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.sqs
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
@pytest.mark.sqs
async def full_broker(settings):
    broker = SQSBroker(
        settings.url,
        region_name=settings.region_name,
        config=AioConfig(signature_version=UNSIGNED),
        response_queue=str(uuid4()),
    )
    yield broker
    await broker.close()


@pytest_asyncio.fixture
async def test_broker():
    broker = SQSBroker()
    yield TestSQSBroker(broker)
