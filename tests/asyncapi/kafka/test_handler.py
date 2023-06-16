from propan import KafkaBroker, PropanApp
from propan.cli.docs.gen import gen_app_schema_json


def test_base_handler():
    broker = KafkaBroker()

    @broker.handle("test")
    async def handler(a: int):
        ...

    schema = gen_app_schema_json(PropanApp(broker))
    assert schema["channels"] == {
        "Handler": {
            "bindings": {"kafka": {"bindingVersion": "0.4.0", "topic": ["test"]}},
            "servers": ["dev"],
            "subscribe": {"message": {"$ref": "#/components/messages/HandlerMessage"}},
        }
    }


def test_group_handler():
    broker = KafkaBroker()

    @broker.handle("test", group_id="workers")
    async def handler(a: int) -> str:
        ...

    schema = gen_app_schema_json(PropanApp(broker))

    examples = schema["channels"]["Handler"]["subscribe"]["bindings"]["kafka"][
        "replyTo"
    ].pop("examples", [])
    if examples and examples[0]:  # pragma: no branch
        assert isinstance(examples[0], str)

    assert schema["channels"] == {
        "Handler": {
            "bindings": {"kafka": {"bindingVersion": "0.4.0", "topic": ["test"]}},
            "servers": ["dev"],
            "subscribe": {
                "bindings": {
                    "kafka": {
                        "bindingVersion": "0.4.0",
                        "groupId": {"enum": ["workers"], "type": "string"},
                        "replyTo": {
                            "title": "HandlerReply",
                            "type": "string",
                        },
                    }
                },
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }
