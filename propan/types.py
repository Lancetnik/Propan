from typing import Any, Awaitable, Callable, Dict, Union

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
