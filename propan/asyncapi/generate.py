from typing import Dict

from propan.app import PropanApp
from propan.asyncapi import (
    Schema,
    Info,
    Server,
    Channel,
)
from propan.constants import ContentTypes


def get_app_schema(app: PropanApp) -> Schema:
    servers = get_app_broker_server(app)
    channels = get_app_broker_channels(app)
    schema = Schema(
        info=Info(
            title=app.title,
            version=app.version,
            description=app.description,
            termsOfService=app.terms_of_service,
            contact=app.contact,
            license=app.license,
        ),
        defaultContentType=ContentTypes.json.value,
        id=app.identifier,
        tags=app.tags,
        externalDocs=app.external_docs,
        servers=servers,
        # TODO
        channels=channels,
        # components
    )
    return schema


def get_app_broker_server(app: PropanApp) -> Dict[str, Server]:
    servers = {}

    broker = app.broker

    broker_meta = {
        "protocol": broker.protocol,
        "protocolVersion": broker.protocol_version,
        "description": broker.description,
        "tags": broker.tags,
    }

    if isinstance(broker.url, str):
        servers["development"] = Server(
            url=broker.url,
            **broker_meta,
            # TODO
            # security
            # variables
            # bindings
        )

    # else:
    #     bunch of them

    return servers


def get_app_broker_channels(app: PropanApp) -> Dict[str, Channel]:
    channels = {}
    for h in app.broker.handlers.values():
        name, channel = h.schema()
        if channel is not None:
            channels[name] = channel
    return channels
