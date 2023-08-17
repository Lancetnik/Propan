from typing import Optional, Type

import pydantic

from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.broker.core.abc import BrokerUsecase


class ArgumentsTestcase:
    broker_class: Type[BrokerUsecase]

    def build_app(self, broker):
        """Patch it to test FastAPI scheme generation too"""
        return PropanApp(broker)

    def test_no_type(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {"HandleMsgPayload": {"title": "HandleMsgPayload"}}

    def test_simple_type(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: int):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandleMsgPayload": {"title": "HandleMsgPayload", "type": "integer"}
        }

    def test_simple_optional_type(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: Optional[int]):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandleMsgPayload": {
                "anyOf": [{"type": "integer"}, {"type": "null"}],
                "title": "HandleMsgPayload",
            }
        }

    def test_simple_type_with_default(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: int = 1):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandleMsgPayload": {
                "default": 1,
                "title": "HandleMsgPayload",
                "type": "integer",
            }
        }

    def test_multi_args_no_type(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg, another):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "properties": {
                    "another": {"title": "Another"},
                    "msg": {"title": "Msg"},
                },
                "required": ["msg", "another"],
                "title": "HandlePayload",
                "type": "object",
            }
        }

    def test_multi_args_with_type(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: str, another: int):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "properties": {
                    "another": {"title": "Another", "type": "integer"},
                    "msg": {"title": "Msg", "type": "string"},
                },
                "required": ["msg", "another"],
                "title": "HandlePayload",
                "type": "object",
            }
        }

    def test_multi_args_with_default(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: str, another: Optional[int] = None):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "properties": {
                    "another": {
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                        "title": "Another",
                    },
                    "msg": {"title": "Msg", "type": "string"},
                },
                "required": ["msg"],
                "title": "HandlePayload",
                "type": "object",
            }
        }

    def test_multi_args_with_pydantic_field(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(
            msg: str,
            another: Optional[pydantic.PositiveInt] = pydantic.Field(
                None, description="some field", title="Perfect"
            ),
        ):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "properties": {
                    "another": {
                        "anyOf": [
                            {"exclusiveMinimum": 0, "type": "integer"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "description": "some field",
                        "title": "Perfect",
                    },
                    "msg": {"title": "Msg", "type": "string"},
                },
                "required": ["msg"],
                "title": "HandlePayload",
                "type": "object",
            }
        }

    def test_pydantic_model(self):
        class User(pydantic.BaseModel):
            name: str = ""
            id: int

        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(user: User):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "User": {
                "properties": {
                    "id": {"title": "Id", "type": "integer"},
                    "name": {"default": "", "title": "Name", "type": "string"},
                },
                "required": ["id"],
                "title": "User",
                "type": "object",
            }
        }

    def test_pydantic_model_mixed_regular(self):
        class User(pydantic.BaseModel):
            name: str = ""
            id: int

        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(user: User, description: str = ""):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "$defs": {
                    "User": {
                        "properties": {
                            "id": {"title": "Id", "type": "integer"},
                            "name": {"default": "", "title": "Name", "type": "string"},
                        },
                        "required": ["id"],
                        "title": "User",
                        "type": "object",
                    }
                },
                "properties": {
                    "description": {
                        "default": "",
                        "title": "Description",
                        "type": "string",
                    },
                    "user": {"$ref": "#/$defs/User"},
                },
                "required": ["user"],
                "title": "HandlePayload",
                "type": "object",
            }
        }

    def test_with_filter(self):
        class User(pydantic.BaseModel):
            name: str = ""
            id: int

        broker = self.broker_class()

        @broker.subscriber(
            "test", filter=lambda m: m.content_type == "application/json"
        )
        async def handle(id: int, description: str = ""):
            ...

        @broker.subscriber("test")
        async def handle_default(msg):
            ...

        schema = get_app_schema(self.build_app(broker)).to_jsonable()

        payload = schema["components"]["schemas"]

        assert payload == {
            "HandlePayload": {
                "oneOf": {
                    "HandleMsgPayload": {"title": "HandleMsgPayload"},
                    "HandlePayload": {
                        "properties": {
                            "description": {
                                "default": "",
                                "title": "Description",
                                "type": "string",
                            },
                            "id": {"title": "Id", "type": "integer"},
                        },
                        "required": ["id"],
                        "title": "HandlePayload",
                        "type": "object",
                    },
                }
            }
        }
