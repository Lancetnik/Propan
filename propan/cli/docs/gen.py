from pathlib import Path

import typer
import yaml

from propan.brokers._model.schemas import ContentTypes
from propan.asyncapi import ASYNC_API_VERSION, AsyncAPIInfo
from propan.cli.app import PropanApp
from propan.types import AnyDict


def generate_doc_file(app: PropanApp, filename: Path) -> None:
    schema = get_app_schema(app)
    with filename.open("w") as f:
        yaml.dump(schema, f, sort_keys=False)
    typer.echo(f"Your project AsyncAPI schema was placed to `{filename}`")


def get_app_schema(app: PropanApp) -> AnyDict:
    schema = {
        "asyncapi": ASYNC_API_VERSION,
        "info": _get_app_info(app),
        "defaultContentType": ContentTypes.json.value,
    }

    return schema


def _get_app_info(app: PropanApp) -> AnyDict:
    return AsyncAPIInfo(
        title=app.title,
        version=app.version,
        description=app.description,
    ).dict()
