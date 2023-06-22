from fast_depends.core import build_call_model
from pydantic import BaseModel

from propan.brokers._model.schemas import BaseHandler


def test_base():
    def func(a: int):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example")
    if example:  # pragma: no branch
        assert isinstance(example, int)
    assert result == {
        "title": "FuncPayload",
        "type": "integer",
    }

    assert response is None


def test_multi_args():
    def func(a: int, b: float):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example", None)
    if example:  # pragma: no branch
        assert isinstance(example["a"], int)
        assert isinstance(example["b"], float)
    assert result == {
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "number"},
        },
        "required": ["a", "b"],
        "title": "FuncPayload",
        "type": "object",
    }

    assert response is None


def test_pydantic_args():
    class Message(BaseModel):
        a: int
        b: float

    def func(a: Message):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example", None)
    if example:  # pragma: no branch
        assert isinstance(example["a"], int)
        assert isinstance(example["b"], float)
    assert result == {
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "number"},
        },
        "required": ["a", "b"],
        "title": "Message",
        "type": "object",
    }

    assert response is None


def test_pydantic_example():
    class Message(BaseModel):
        a: int

        class Config:
            schema_extra = {"example": {"a": 1}}

    def func(a: Message):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"
    assert result == {
        "example": {"a": 1},
        "properties": {
            "a": {"title": "A", "type": "integer"},
        },
        "required": ["a"],
        "title": "Message",
        "type": "object",
    }

    assert response is None


def test_response_base():
    def func() -> str:
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"
    assert result == {
        "title": "FuncPayload",
        "type": "null",
    }

    for r in response.pop("examples", []):
        if r:  # pragma: no branch
            assert isinstance(r, str)

    assert response == {"title": "FuncReply", "type": "string"}


def test_pydantic_response():
    class Message(BaseModel):
        a: int

        class Config:
            schema_extra = {"example": {"a": 1}}

    def func() -> Message:
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"
    assert result == {
        "title": "FuncPayload",
        "type": "null",
    }

    assert response == {
        "examples": [{"a": 1}],
        "properties": {
            "a": {"title": "A", "type": "integer"},
        },
        "required": ["a"],
        "title": "Message",
        "type": "object",
    }


def test_pydantic_gen_response_examples():
    class Message(BaseModel):
        a: int

    def func() -> Message:
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"
    assert result == {
        "title": "FuncPayload",
        "type": "null",
    }

    for r in response.pop("examples", []):
        if r:  # pragma: no branch
            assert isinstance(r["a"], int)

    assert response == {
        "properties": {
            "a": {"title": "A", "type": "integer"},
        },
        "required": ["a"],
        "title": "Message",
        "type": "object",
    }
