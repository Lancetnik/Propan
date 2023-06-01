from pathlib import Path

import typer
import yaml

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import ContentTypes
from propan.asyncapi import (ASYNC_API_VERSION, AsyncAPIInfo, AsyncAPIServer,)
from propan.cli.app import PropanApp
from propan.types import AnyDict


def generate_doc_file(app: PropanApp, filename: Path) -> None:
    if app.broker is None:
        typer.echo("Your PropanApp has no broker")
        raise typer.Exit()

    schema = get_app_schema(app)
    with filename.open("w") as f:
        yaml.dump(schema, f, sort_keys=False)
    typer.echo(f"Your project AsyncAPI schema was placed to `{filename}`")


def get_app_schema(app: PropanApp) -> AnyDict:
    schema = {
        "asyncapi": ASYNC_API_VERSION,
        "defaultContentType": ContentTypes.json.value,
        "info": _get_app_info(app),
        "servers": _get_broker_servers(app.broker),
        "channels": _get_broker_channels(app.broker),
    }

    return schema


def _get_app_info(app: PropanApp) -> AnyDict:
    return AsyncAPIInfo(
        title=app.title,
        version=app.version,
        description=app.description,
    ).dict()


def _get_broker_servers(broker: BrokerUsecase) -> AnyDict:
    return {
        "production": AsyncAPIServer(
            url=broker.url,
            protocol=broker.protocol,
        ).dict()
    }


def _get_broker_channels(broker: BrokerUsecase) -> AnyDict:
    channels = {}
    for handler in broker.handlers:
        name, data = handler.get_schema()
        channels[name] = data
    return channels
