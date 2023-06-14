from propan import PropanApp, SQSBroker
from propan.cli.docs.gen import gen_app_schema_json


def test_base_handler():
    broker = SQSBroker()

    @broker.handle("test")
    async def handler(a: int):
        ...

    schema = gen_app_schema_json(PropanApp(broker))

    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "sqs": {
                    "bindingVersion": "custom",
                    "queue": {"fifo": False, "name": "test"},
                }
            },
            "servers": ["dev"],
            "subscribe": {
                "bindings": {"sqs": {"bindingVersion": "custom"}},
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }


def test_group_handler():
    broker = SQSBroker()

    @broker.handle("test")
    async def handler(a: int) -> str:
        ...

    schema = gen_app_schema_json(PropanApp(broker))

    examples = schema["channels"]["Handler"]["subscribe"]["bindings"]["sqs"][
        "replyTo"
    ].pop("examples")
    if examples:
        assert isinstance(
            examples[0],
            str,
        )

    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "sqs": {
                    "bindingVersion": "custom",
                    "queue": {"fifo": False, "name": "test"},
                }
            },
            "servers": ["dev"],
            "subscribe": {
                "bindings": {
                    "sqs": {
                        "bindingVersion": "custom",
                        "replyTo": {"title": "HandlerReply", "type": "string"},
                    }
                },
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }
