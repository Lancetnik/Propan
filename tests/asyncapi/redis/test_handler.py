from propan import PropanApp, RedisBroker
from propan.cli.docs.gen import get_schema_json


def test_base_handler():
    broker = RedisBroker()

    @broker.handle("test")
    async def handler(a: int):
        ...

    schema = get_schema_json(PropanApp(broker))

    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "redis": {
                    "bindingVersion": "custom",
                    "channel": "test",
                    "method": "subscribe",
                }
            },
            "servers": ["dev"],
            "subscribe": {
                "bindings": {"redis": {"bindingVersion": "custom"}},
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }


def test_group_handler():
    broker = RedisBroker()

    @broker.handle("*test", pattern=True)
    async def handler(a: int) -> str:
        ...

    schema = get_schema_json(PropanApp(broker))

    assert isinstance(
        schema["channels"]["Handler"]["subscribe"]["bindings"]["redis"]["replyTo"].pop(
            "examples"
        )[0],
        str,
    )

    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "redis": {
                    "bindingVersion": "custom",
                    "channel": "*test",
                    "method": "psubscribe",
                }
            },
            "servers": ["dev"],
            "subscribe": {
                "bindings": {
                    "redis": {
                        "bindingVersion": "custom",
                        "replyTo": {"title": "HandlerReply", "type": "string"},
                    }
                },
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }
