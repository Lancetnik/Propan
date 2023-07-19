from typing import Any, Callable, Dict, Generic, List, Optional, Type, Union, overload
from unittest.mock import MagicMock

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
    mock: MagicMock
    response_mocks: Dict[str, MagicMock]

    _original_call: Callable[P_HandlerParams, T_HandlerReturn]
    _publishers: List[Any]

    def __init__(self, call: Callable[P_HandlerParams, T_HandlerReturn]):
        if isinstance(call, HandlerCallWrapper):
            self._original_call = call._original_call
            self._publishers = call._publishers
            self.response_mocks = call.response_mocks
            self.mock = call.mock
        else:
            self._original_call = call
            self._publishers = []
            self.mock = MagicMock()
            self.response_mocks = {}
        self.__name__ = getattr(self._original_call, "__name__", "undefined")

    def __hash__(self) -> int:
        return hash(self._original_call)

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        self.mock(*args, **kwargs)
        return self._original_call(*args, **kwargs)


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]
