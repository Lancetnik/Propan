from typing import Any, Awaitable, Callable, Coroutine, Dict, Union

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
DecodedMessage: TypeAlias = Union[str, AnyDict, bytes]
SendableMessage: TypeAlias = Union[DecodedMessage, BaseModel, None]

HandlerWrapper: TypeAlias = Callable[
    [Callable[..., Coroutine[Any, Any, SendableMessage]]],
    Callable[..., SendableMessage],
]
