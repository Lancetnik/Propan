from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional, Type, Union, overload
from unittest.mock import MagicMock

from pydantic import BaseModel, Field, Json
from typing_extensions import Self, TypeVar

from propan.asyncapi.base import AsyncAPIOperation
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.types import AnyDict, DecodedMessage, DecoratedCallable, SendableMessage

Cls = TypeVar("Cls")
NameRequiredCls = TypeVar("NameRequiredCls", bound="NameRequired")


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __eq__(self, __value: object) -> bool:
        if __value is None:
            return False

        if not isinstance(__value, NameRequired):
            return NotImplemented

        return self.name == __value.name

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    @overload
    @classmethod
    def validate(
        cls: Type[NameRequiredCls], value: Union[str, NameRequiredCls]
    ) -> NameRequiredCls:
        ...

    @overload
    @classmethod
    def validate(cls: Type[NameRequiredCls], value: None) -> None:
        ...

    @classmethod
    def validate(
        cls: Type[NameRequiredCls], value: Union[str, NameRequiredCls, None]
    ) -> Optional[NameRequiredCls]:
        if value is not None:
            if isinstance(value, str):
                value = cls(value)
        return value


class HandlerCallWrapper(Generic[P_HandlerParams, T_HandlerReturn]):
    mock: MagicMock

    _wrapped_call: Optional[DecoratedCallable]
    _original_call: Callable[P_HandlerParams, T_HandlerReturn]
    _publishers: List["Publisher"]

    def __new__(
        cls,
        call: Union[
            "HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]",
            Callable[P_HandlerParams, T_HandlerReturn],
        ],
    ) -> Self:
        if isinstance(call, cls):
            return call
        else:
            return super().__new__(cls)

    def __init__(
        self,
        call: Callable[P_HandlerParams, T_HandlerReturn],
    ):
        if not isinstance(call, HandlerCallWrapper):
            self._original_call = call
            self._wrapped_call = None
            self._publishers = []
            self.mock = MagicMock()
            self.__name__ = getattr(self._original_call, "__name__", "undefined")

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        self.mock(*args, **kwargs)
        return self._original_call(*args, **kwargs)


@dataclass
class Publisher(AsyncAPIOperation):
    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)

    calls: List[Callable[..., Any]] = field(
        init=False, default_factory=list, repr=False
    )
    mock: MagicMock = field(init=False, default_factory=MagicMock, repr=False)

    @property
    def channel_title(self) -> str:
        return self.title or self.calls[0].__name__.replace("_", " ").title().replace(
            " ", ""
        )

    def __call__(
        self,
        func: Callable[P_HandlerParams, T_HandlerReturn],
    ) -> HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]:
        handler_call = HandlerCallWrapper(func)
        handler_call._publishers.append(self)
        self.calls.append(handler_call._original_call)
        return handler_call

    @abstractmethod
    def publish(
        self,
        message: SendableMessage,
        correlation_id: Optional[str] = None,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        raise NotImplementedError()


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]
