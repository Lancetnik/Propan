from typing import Any, Optional, Type, Union, overload

from pydantic import BaseModel, Field, Json
from typing_extensions import TypeVar

Cls = TypeVar("Cls")


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __eq__(self, __value: Optional["NameRequired"]) -> bool:
        return __value and self.name == __value.name

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    @overload
    @classmethod
    def validate(cls: Type[Cls], value: None = None) -> None:
        ...

    @overload
    @classmethod
    def validate(cls: Type[Cls], value: Union[str, Cls]) -> Cls:
        ...

    @classmethod
    def validate(cls: Type[Cls], value: Union[str, Cls, None]) -> Optional[Cls]:
        if value is not None:
            if isinstance(value, str):
                value = cls(value)
        return value


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]
