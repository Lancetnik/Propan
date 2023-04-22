from typing import Any, Callable, Dict, TypeVar, Union

from fast_depends.types import AnyCallable, AnyDict, DecoratedCallable, P

__all__ = (
    "DecoratedCallable",
    "P",
    "AnyDict",
    "AnyCallable",
    "DecodedMessage",
    "DecoratedCallableNone" "Wrapper",
)

DecoratedCallableNone = TypeVar("DecoratedCallableNone", bound=Callable[..., None])

Wrapper = Callable[[DecoratedCallable], DecoratedCallable]
DecodedMessage = Union[str, Dict[str, Any], bytes]
