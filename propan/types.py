from typing import Any, Callable, Dict, TypeVar, Union

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])
DecoratedCallableNone = TypeVar("DecoratedCallableNone", bound=Callable[..., None])

Wrapper = Callable[[DecoratedCallable], DecoratedCallable]
DecodedMessage = Union[str, Dict[str, Any], bytes]
