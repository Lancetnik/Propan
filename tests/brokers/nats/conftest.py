import pytest
import pytest_asyncio
from pydantic import BaseSettings

from propan import NatsBroker


class Settings(BaseSettings):
    url = "nats://localhost:4222"


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest_asyncio.fixture
@pytest.mark.kafka
async def broker(settings):
    broker = NatsBroker(settings.url, apply_types=False)
    yield broker
    await broker.close()
