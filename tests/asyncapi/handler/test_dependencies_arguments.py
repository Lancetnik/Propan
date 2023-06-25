from fast_depends.core import build_call_model

from propan import Depends
from propan.brokers._model.schemas import BaseHandler


def test_base():
    def dep(a: int):
        ...

    def func(a=Depends(dep)):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example", None)
    if example:  # pragma: no branch
        assert isinstance(example, int)
    assert result == {
        "title": "FuncPayload",
        "type": "integer",
    }

    assert response is None


def test_multi_args():
    def dep2(c: int):
        ...

    def dep(a: int, m=Depends(dep2)):
        ...

    def func(b: float, d=Depends(dep)):
        ...

    handler = BaseHandler(func, build_call_model(call=func))

    message_title, result, response = handler.get_message_object()

    assert message_title == "FuncMessage"

    example = result.pop("example", None)
    if example:  # pragma: no branch
        assert isinstance(example["a"], int)
        assert isinstance(example["c"], int)
        assert isinstance(example["b"], float)

    assert set(result.pop("required")) == {"b", "a", "c"}
    assert result == {
        "properties": {
            "a": {"title": "A", "type": "integer"},
            "b": {"title": "B", "type": "number"},
            "c": {"title": "C", "type": "integer"},
        },
        "title": "FuncPayload",
        "type": "object",
    }

    assert response is None
