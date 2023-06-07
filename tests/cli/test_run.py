from pathlib import Path
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from propan import PropanApp
from propan.cli import cli


@pytest.mark.rabbit
def test_run_rabbit_correct(
    runner: CliRunner,
    rabbit_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f"{rabbit_async_project.name}.app.serve:app"

    async def patched_run(self: PropanApp, *args, **kwargs):
        await self._startup()
        await self._shutdown()
        mock()

    with monkeypatch.context() as m:
        m.setattr(PropanApp, "run", patched_run)
        r = runner.invoke(cli, ["run", app_path])

    assert r.exit_code == 0
    mock.assert_called_once()


@pytest.mark.redis
def test_run_redis_correct(
    runner: CliRunner,
    redis_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f"{redis_async_project.name}.app.serve:app"

    async def patched_run(self: PropanApp, *args, **kwargs):
        await self._startup()
        await self._shutdown()
        mock()

    with monkeypatch.context() as m:
        m.setattr(PropanApp, "run", patched_run)
        r = runner.invoke(cli, ["run", app_path])

        assert r.exit_code == 0
        mock.assert_called_once()


@pytest.mark.nats
def test_run_nats_correct(
    runner: CliRunner,
    nats_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f"{nats_async_project.name}.app.serve:app"

    async def patched_run(self: PropanApp, *args, **kwargs):
        await self._startup()
        await self._shutdown()
        mock()

    with monkeypatch.context() as m:
        m.setattr(PropanApp, "run", patched_run)
        r = runner.invoke(cli, ["run", app_path])

    assert r.exit_code == 0
    mock.assert_called_once()


@pytest.mark.kafka
def test_run_kafka_correct(
    runner: CliRunner,
    kafka_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f"{kafka_async_project.name}.app.serve:app"

    async def patched_run(self: PropanApp, *args, **kwargs):
        await self._startup()
        await self._shutdown()
        mock()

    with monkeypatch.context() as m:
        m.setattr(PropanApp, "run", patched_run)
        r = runner.invoke(cli, ["run", app_path])

    assert r.exit_code == 0
    mock.assert_called_once()


@pytest.mark.sqs
@pytest.mark.xfail  # TODO: fix it
def test_run_sqs_correct(
    runner: CliRunner,
    sqs_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f"{sqs_async_project.name}.app.serve:app"

    async def patched_run(self: PropanApp, *args, **kwargs):
        await self._startup()
        await self._shutdown()
        mock()

    with monkeypatch.context() as m:
        m.setattr(PropanApp, "run", patched_run)
        r = runner.invoke(cli, ["run", app_path])

    assert r.exit_code == 0
    mock.assert_called_once()
