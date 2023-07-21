from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Type, Union, overload
from unittest.mock import MagicMock

from pydantic import BaseModel, Field, Json
from typing_extensions import TypeVar

from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.types import DecodedMessage, DecoratedCallable, SendableMessage

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

    _wrapped_call: Optional[DecoratedCallable]
    _original_call: Callable[P_HandlerParams, T_HandlerReturn]
    _publishers: List["Publisher"]

    def __new__(
        cls,
        call: Callable[P_HandlerParams, T_HandlerReturn],
    ):
        if isinstance(call, HandlerCallWrapper):
            return call
        else:
            return super().__new__(cls)

    def __hash__(self) -> int:
        return hash(self._original_call)

    def __init__(
        self,
        call: Callable[P_HandlerParams, T_HandlerReturn],
    ):
        if not isinstance(call, HandlerCallWrapper):
            self._original_call = call
            self._wrapped_call = None
            self._publishers = []
            self.mock = MagicMock()
            self.response_mocks = {}
            self.__name__ = getattr(self._original_call, "__name__", "undefined")

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        self.mock(*args, **kwargs)
        return self._original_call(*args, **kwargs)


@dataclass
class Publisher:
    mock: MagicMock = field(init=False, default_factory=MagicMock, repr=False)

    def __call__(
        self,
        func: Callable[P_HandlerParams, T_HandlerReturn],
    ) -> HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]:
        handler_call = HandlerCallWrapper(func)
        handler_call._publishers.append(self)
        return handler_call

    @abstractmethod
    def publish(self, message: SendableMessage) -> Optional[DecodedMessage]:
        raise NotImplementedError()


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]
