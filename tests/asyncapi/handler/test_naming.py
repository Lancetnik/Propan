from fast_depends.construct import get_dependant
from pydantic import Field

from propan.brokers._model.schemas import BaseHandler


def test_pydantic_field_rename():
    def func(a: int = Field(title="MyField", description="MyField")):
        ...

    handler = BaseHandler(func, get_dependant(path="", call=func))

    _, result, _ = handler.get_message_object()

    assert result["description"] == result["title"] == "MyField"
    assert result["title"] == "MyField"


def test_pydantic_field_rename_miltiple():
    def func(
        a: int = Field(title="AField", description="AField"),
        b: str = Field("", title="BField", description="BField"),
    ):
        ...

    handler = BaseHandler(func, get_dependant(path="", call=func))

    _, result, _ = handler.get_message_object()

    assert (
        result["properties"]["b"]["title"]
        == result["properties"]["b"]["description"]
        == "BField"
    )
    assert (
        result["properties"]["a"]["title"]
        == result["properties"]["a"]["description"]
        == "AField"
    )
