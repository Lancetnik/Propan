from pathlib import Path

import pytest
from typer.testing import CliRunner

from propan import PropanApp
from propan.cli import cli


@pytest.fixture()
def broker():
    # separate import from e2e tests
    from propan.brokers.rabbit import RabbitBroker
    yield RabbitBroker()


@pytest.fixture()
def app_without_logger(broker):
    return PropanApp(broker, None)


@pytest.fixture()
def app_without_broker():
    return PropanApp()


@pytest.fixture()
def app(broker):
    return PropanApp(broker)


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture(scope="session")
def rabbit_async_project(runner: CliRunner) -> Path:
    project_name = "rabbit"
    runner.invoke(cli, ["create", "async", "rabbit", project_name])
    yield Path.cwd() / Path(project_name)


@pytest.fixture(scope="session")
def redis_async_project(runner: CliRunner) -> Path:
    project_name = "redis"
    runner.invoke(cli, ["create", "async", "redis", project_name])
    yield Path.cwd() / Path(project_name)


@pytest.fixture(scope="session")
def nats_async_project(runner: CliRunner) -> Path:
    project_name = "nats"
    runner.invoke(cli, ["create", "async", "nats", project_name])
    yield Path.cwd() / Path(project_name)


@pytest.fixture(scope="session")
def kafka_async_project(runner: CliRunner) -> Path:
    project_name = "kafka"
    runner.invoke(cli, ["create", "async", "kafka", project_name])
    yield Path.cwd() / Path(project_name)


@pytest.fixture(scope="session")
def sqs_async_project(runner: CliRunner) -> Path:
    project_name = "sqs"
    runner.invoke(cli, ["create", "async", "sqs", project_name])
    yield Path.cwd() / Path(project_name)
