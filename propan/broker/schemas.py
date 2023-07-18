from unittest.mock import MagicMock
from typing import Any, Optional, Type, Union, overload, Generic, Callable, Dict

from pydantic import BaseModel, Field, Json
from typing_extensions import TypeVar

from propan.broker.types import P_HandlerParams, T_HandlerReturn


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


class HandlerCallWrapper(Generic[P_HandlerParams, T_HandlerReturn]):
    original_call: Callable[P_HandlerParams, T_HandlerReturn]
    mock: MagicMock
    responses: Dict[str, Any]

    def __init__(self, call: Union[
        Callable[P_HandlerParams, T_HandlerReturn],
        "HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]"
    ]):
        if isinstance(call, HandlerCallWrapper):
            self.original_call = call.original_call
            self.responses = call.responses
        else:
            self.original_call = call
            self.responses = {}
        self.__name__ = getattr(self.original_call, "__name__", "undefined")
        self.mock = MagicMock()

    def __hash__(self) -> int:
        return hash(self.original_call)

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        self.mock(*args, **kwargs)
        return self.original_call(*args, **kwargs)


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]
