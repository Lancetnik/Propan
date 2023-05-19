from tempfile import TemporaryDirectory

import pytest
from typer.testing import CliRunner

from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.cli.startproject.async_app.rabbit import create_rabbit
from propan.cli.startproject.async_app.redis import create_redis
from propan.cli.startproject.async_app.nats import create_nats


@pytest.fixture
def broker():
    yield RabbitBroker()


@pytest.fixture
def app_without_logger(broker):
    return PropanApp(broker, None)


@pytest.fixture
def app_without_broker():
    return PropanApp()


@pytest.fixture
def app(broker):
    return PropanApp(broker)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(scope="module")
def rabbit_async_project():
    with TemporaryDirectory() as dir:
        yield create_rabbit(dir)


@pytest.fixture(scope="module")
def redis_async_project():
    with TemporaryDirectory() as dir:
        yield create_redis(dir)


@pytest.fixture(scope="module")
def nats_async_project():
    with TemporaryDirectory() as dir:
        yield create_nats(dir)
