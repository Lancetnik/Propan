import json
from io import StringIO
from pathlib import Path
from typing import Dict, cast

import typer

from propan.asyncapi import (
    AsyncAPIChannel,
    AsyncAPIComponents,
    AsyncAPIInfo,
    AsyncAPIMessage,
    AsyncAPISchema,
    AsyncAPIServer,
)
from propan.brokers._model import BrokerUsecase
from propan.cli.app import PropanApp
from propan.types import AnyDict


def generate_doc_file(app: PropanApp, filename: Path) -> None:
    schema = get_schema_yaml(app)
    filename.write_text(schema)
    typer.echo(f"Your project AsyncAPI schema was placed to `{filename}`")


def get_schema_yaml(app: PropanApp) -> str:
    try:
        import yaml
    except ImportError as e:  # pragma: no cover
        typer.echo(
            "To generate documentation, please install the dependencies\n"
            'pip install "propan[doc]"'
        )
        raise typer.Exit(1) from e

    if app.broker is None:
        raise typer.BadParameter("Your PropanApp has no broker")

    schema = get_schema_json(app)
    io = StringIO(initial_value="", newline="\n")
    yaml.dump(schema, io, sort_keys=False)
    return io.getvalue()


def get_schema_json(app: PropanApp) -> AnyDict:
    return cast(
        AnyDict,
        json.loads(
            get_app_schema(app).json(
                by_alias=True,
                exclude_none=True,
            )
        ),
    )


def get_app_schema(app: PropanApp) -> AsyncAPISchema:
    if not isinstance(app.broker, BrokerUsecase):
        raise typer.BadParameter("Your PropanApp broker is invalid")

    servers = _get_broker_servers(app.broker)

    messages: Dict[str, AsyncAPIMessage] = {}
    payloads: Dict[str, AnyDict] = {}

    channels = _get_broker_channels(app.broker)
    for ch in channels.values():
        ch.servers = list(servers.keys())

        if ch.subscribe is not None:  # pragma: no branch
            m = ch.subscribe.message
            m_title = m.title or "Message"

            p = m.payload
            p_title = p.get("title", m_title)
            payloads[p_title] = p

            m.payload = {"$ref": f"#/components/schemas/{p_title}"}

            messages[m_title] = m
            ch.subscribe.message = {"$ref": f"#/components/messages/{m_title}"}  # type: ignore

    schema = AsyncAPISchema(
        info=_get_app_info(app),
        servers=servers,
        channels=channels,
        components=AsyncAPIComponents(
            messages=messages,
            schemas=payloads,
        ),
    )
    return schema


def _get_app_info(app: PropanApp) -> AsyncAPIInfo:
    return AsyncAPIInfo(
        title=app.title,
        version=app.version,
        description=app.description,
        license=app.license,
        contact=app.contact,
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
            protocolVersion=broker.protocol_version,
        )
    }


def _get_broker_channels(broker: BrokerUsecase) -> Dict[str, AsyncAPIChannel]:
    channels = {}
    for handler in broker.handlers:
        channels.update(handler.get_schema())

    return channels
