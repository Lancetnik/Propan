from typing import Any, Dict

from propan.app import PropanApp
from propan.asyncapi import Channel, Components, Info, Message, Schema, Server
from propan.constants import ContentTypes


def get_app_schema(app: PropanApp) -> Schema:
    servers = get_app_broker_server(app)
    channels = get_app_broker_channels(app)

    messages: Dict[str, Message] = {}
    payloads: Dict[str, Dict[str, Any]] = {}
    for channel_name, ch in channels.items():
        ch.servers = list(servers.keys())

        if ch.subscribe is not None:  # pragma: no branch
            m = ch.subscribe.message

            p = m.payload
            p_title = p.get("title", f"{channel_name}Payload")
            payloads[p_title] = p
            m.payload = {"$ref": f"#/components/schemas/{p_title}"}

            assert m.title
            messages[m.title] = m
            ch.subscribe.message = {
                "$ref": f"#/components/messages/{m.title}"
            }  # type: ignore

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
        tags=list(app.tags) if app.tags else None,
        externalDocs=app.external_docs,
        servers=servers,
        channels=channels,
        components=Components(
            messages=messages,
            schemas=payloads,
        ),
    )
    return schema


def get_app_broker_server(app: PropanApp) -> Dict[str, Server]:
    servers = {}

    broker = app.broker
    assert broker

    broker_meta = {
        "protocol": broker.protocol,
        "protocolVersion": broker.protocol_version,
        "description": broker.description,
        "tags": broker.tags,
    }

    if isinstance(broker.url, str):
        servers["development"] = Server(
            url=broker.url,
            **broker_meta,  # type: ignore[arg-type]
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
    assert app.broker
    for h in app.broker.handlers.values():
        name, channel = h.schema()
        if channel is not None:
            channels[name] = channel

    for p in app.broker._publishers.values():
        name, channel = p.schema()
        if channel is not None:
            channels[name] = channel

    return channels
