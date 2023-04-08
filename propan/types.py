from typing import Any, Callable, TypeVar

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])
DecoratedCallableNone = TypeVar("DecoratedCallableNone", bound=Callable[..., None])
