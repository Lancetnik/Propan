from pathlib import Path
from typing import Dict
from io import StringIO

import typer

from propan.asyncapi import (
    AsyncAPIChannel,
    AsyncAPIInfo,
    AsyncAPISchema,
    AsyncAPIServer,
)
from propan.brokers._model import BrokerUsecase
from propan.cli.app import PropanApp


def generate_doc_file(app: PropanApp, filename: Path) -> None:
    schema = get_schema_yaml(app)
    filename.write_text(schema)
    typer.echo(f"Your project AsyncAPI schema was placed to `{filename}`")


def get_schema_yaml(app: PropanApp) -> str:
    try:
        import yaml
    except ImportError as e:
        typer.echo(
            "To generate documentation, please install the dependencies\n"
            'pip install "propan[doc]"'
        )
        raise typer.Exit() from e

    if app.broker is None:
        typer.echo("Your PropanApp has no broker")
        raise typer.Exit()

    schema = get_app_schema(app).dict(
        by_alias=True,
        exclude_none=True,
    )

    io = StringIO(initial_value="", newline="\n")
    yaml.dump(schema, io, sort_keys=False)
    return io.getvalue()


def get_app_schema(app: PropanApp) -> AsyncAPISchema:
    if not isinstance(app.broker, BrokerUsecase):
        typer.echo("Your PropanApp broker is invalid")
        raise typer.Exit()

    servers = _get_broker_servers(app.broker)

    channels = _get_broker_channels(app.broker)
    for ch in channels.values():
        ch.servers = list(servers.keys())

    schema = AsyncAPISchema(
        info=_get_app_info(app),
        servers=servers,
        channels=channels,
    )
    return schema


def _get_app_info(app: PropanApp) -> AsyncAPIInfo:
    return AsyncAPIInfo(
        title=app.title,
        version=app.version,
        description=app.description,
    )


def _get_broker_servers(broker: BrokerUsecase) -> Dict[str, AsyncAPIServer]:
    if isinstance(broker.url, str):
        url = broker.url
    else:
        url = broker.url[0]

    return {
        "dev": AsyncAPIServer(
            url=url,
            protocol=broker.protocol,
        )
    }


def _get_broker_channels(broker: BrokerUsecase) -> Dict[str, AsyncAPIChannel]:
    channels = {}
    for handler in broker.handlers:
        channels.update(handler.get_schema())

    return channels
