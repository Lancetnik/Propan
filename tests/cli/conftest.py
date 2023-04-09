from tempfile import TemporaryDirectory

import pytest
from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker
from propan.cli.startproject import create
from typer.testing import CliRunner


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
def project_dir(version):
    with TemporaryDirectory() as dir:
        yield create(dir, version)
