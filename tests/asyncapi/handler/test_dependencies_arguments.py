from fast_depends.construct import get_dependant

from propan import Depends
from propan.brokers._model.schemas import BaseHandler


def test_base():
    def dep(a: int):
        ...

    def func(a=Depends(dep)):
        ...

    handler = BaseHandler(func, get_dependant(path="", call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    assert isinstance(result.pop("example"), int)
    assert result == {
        "title": "FuncPayload",
        "type": "integer",
    }

    assert response is None


def test_multi_args():
    def dep2(c: int):
        ...

    def dep(a: int, _=Depends(dep2)):
        ...

    def func(b: float, _=Depends(dep)):
        ...

    handler = BaseHandler(func, get_dependant(path="", call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example")
    assert isinstance(example["a"], int)
    assert isinstance(example["c"], int)
    assert isinstance(example["b"], float)
    assert result == {
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "number"},
            "c": {"title": "C", "type": "integer"},
        },
        "required": ["b", "a", "c"],
        "title": "FuncPayload",
        "type": "object",
    }

    assert response is None
