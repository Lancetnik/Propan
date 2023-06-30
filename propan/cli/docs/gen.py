from io import StringIO
from pathlib import Path
from typing import Any, Dict, cast

import typer

from propan._compat import model_to_jsonable
from propan.asyncapi import (
    AsyncAPIChannel,
    AsyncAPIComponents,
    AsyncAPIInfo,
    AsyncAPIMessage,
    AsyncAPISchema,
    AsyncAPIServer,
)
from propan.brokers._model import BrokerAsyncUsecase
from propan.cli.app import PropanApp
from propan.types import AnyDict


def generate_doc_file(app: PropanApp, filename: Path) -> None:
    schema = get_app_schema(app)
    json_schema = schema_to_json(schema)
    yaml_schema = json_schema_to_yaml(json_schema)
    filename.write_text(yaml_schema)
    typer.echo(f"Your project AsyncAPI scheme was placed to `{filename}`")


def gen_app_schema_yaml(app: PropanApp) -> str:
    json_schema = gen_app_schema_json(app)
    return json_schema_to_yaml(json_schema)


def gen_app_schema_json(app: PropanApp) -> AnyDict:
    schema = get_app_schema(app)
    return schema_to_json(schema)


def json_schema_to_yaml(schema: AnyDict) -> str:
    try:
        import yaml
    except ImportError as e:  # pragma: no cover
        typer.echo(
            "To generate documentation, please install the dependencies\n"
            'pip install "propan[doc]"'
        )
        raise typer.Exit(1) from e

    io = StringIO(initial_value="", newline="\n")
    yaml.dump(schema, io, sort_keys=False)
    return io.getvalue()


def schema_to_json(schema: AsyncAPISchema) -> AnyDict:
    return cast(
        AnyDict,
        model_to_jsonable(
            schema,
            by_alias=True,
            exclude_none=True,
        ),
    )


def get_app_schema(app: PropanApp) -> AsyncAPISchema:
    if not isinstance(app.broker, BrokerAsyncUsecase):
        raise typer.BadParameter("Your PropanApp broker is invalid")

    servers = _get_broker_servers(app.broker)

    messages: Dict[str, AsyncAPIMessage] = {}
    payloads: Dict[str, AnyDict] = {}

    channels = _get_broker_channels(app.broker)
    for channel_name, ch in channels.items():
        ch.servers = list(servers.keys())

        if ch.subscribe is not None:  # pragma: no branch
            m = ch.subscribe.message
            m_title = m.title or f"{channel_name}Message"

            p = m.payload
            p_title = p.get("title", f"{channel_name}Payload")
            payloads[p_title] = p

            m.payload = {"$ref": f"#/components/schemas/{p_title}"}

            messages[m_title] = m
            ch.subscribe.message = {
                "$ref": f"#/components/messages/{m_title}"
            }  # type: ignore

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
        license=getattr(app, "license", None),
        contact=getattr(app, "contact", None),
    )


def _get_broker_servers(
    broker: BrokerAsyncUsecase[Any, Any]
) -> Dict[str, AsyncAPIServer]:
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


def _get_broker_channels(
    broker: BrokerAsyncUsecase[Any, Any]
) -> Dict[str, AsyncAPIChannel]:
    channels = {}
    for handler in broker.handlers:
        channels.update(handler.get_schema())

    return channels
