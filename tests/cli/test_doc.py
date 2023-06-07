from pathlib import Path
from unittest.mock import Mock

import uvicorn
import yaml
from typer.testing import CliRunner

from propan.cli.main import cli


def test_gen_rabbit_docs(runner: CliRunner, rabbit_async_project: Path):
    app_path = f'{rabbit_async_project / "app" / "serve"}:app'
    r = runner.invoke(cli, ["docs", "gen", app_path])
    assert r.exit_code == 0

    schema_path = rabbit_async_project.parent / "asyncapi.yaml"
    assert schema_path.exists()

    with schema_path.open("r") as f:
        schema = yaml.load(f, Loader=yaml.BaseLoader)

    assert schema


def test_gen_wrong_path(runner: CliRunner, rabbit_async_project: Path):
    app_path = f'{rabbit_async_project / "app" / "serve"}:app1'
    r = runner.invoke(cli, ["docs", "gen", app_path])
    assert r.exit_code == 2
    assert "Please, input module like [python_file:propan_app_name]" in r.stdout


def test_serve_rabbit_docs(
    runner: CliRunner,
    rabbit_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    app_path = f'{rabbit_async_project / "app" / "serve"}:app'

    with monkeypatch.context() as m:
        m.setattr(uvicorn, "run", mock)
        r = runner.invoke(cli, ["docs", "serve", app_path])

    assert r.exit_code == 0
    mock.assert_called_once()


def test_serve_rabbit_schema(
    runner: CliRunner,
    rabbit_async_project: Path,
    monkeypatch,
    mock: Mock,
):
    with monkeypatch.context() as m:
        m.setattr(uvicorn, "run", mock)
        r = runner.invoke(cli, ["docs", "serve", "asyncapi.yaml"])

    assert r.exit_code == 0
    mock.assert_called_once()
