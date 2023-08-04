from dataclasses import dataclass
from uuid import uuid4

import pytest

from propan.brokers.rabbit import RabbitSyncBroker, RabbitExchange, RabbitRouter
from propan.test import TestRabbitSyncBroker


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
def router():
    return RabbitRouter()


@pytest.fixture
def exchange():
    name = str(uuid4())
    return RabbitExchange(name=name)


@pytest.fixture(scope="session")
def settings():
    return Settings()


@pytest.fixture
@pytest.mark.rabbit
def broker(settings):
    broker = RabbitSyncBroker(settings.url, apply_types=False)
    yield broker
    broker.close()


@pytest.fixture
@pytest.mark.rabbit
def full_broker(settings):
    broker = RabbitSyncBroker(settings.url)
    yield broker
    broker.close()


@pytest.fixture
def test_broker():
    broker = RabbitSyncBroker()
    yield TestRabbitSyncBroker(broker)
    broker.close()
