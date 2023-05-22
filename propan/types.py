from typing import Any, Awaitable, Callable, Dict, Sequence, Union

from pydantic import BaseModel
from typing_extensions import TypeAlias

AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]

AnyDict: TypeAlias = Dict[str, Any]
AnyCallable: TypeAlias = Callable[..., Any]
NoneCallable: TypeAlias = Callable[..., None]

DecoratedCallable: TypeAlias = AnyCallable
DecoratedCallableNone: TypeAlias = NoneCallable
DecoratedAsync: TypeAlias = AsyncFunc

Wrapper: TypeAlias = Callable[[AnyCallable], DecoratedCallable]
AsyncWrapper: TypeAlias = Callable[[AnyCallable], DecoratedAsync]
DecodedMessage: TypeAlias = Union[AnyDict, Sequence[Any], str, bytes]
SendableMessage: TypeAlias = Union[DecodedMessage, BaseModel, None]

HandlerCallable: TypeAlias = Callable[
    ...,
    Union[Awaitable[SendableMessage], SendableMessage],
]
HandlerWrapper: TypeAlias = Callable[
    [HandlerCallable],
    HandlerCallable,
]
