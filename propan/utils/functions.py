from functools import wraps
from typing import Awaitable, Callable, TypeVar

from fast_depends.injector import run_async as call_or_await
from typing_extensions import ParamSpec

__all__ = (
    "call_or_await",
    "to_async",
)


T = TypeVar("T")
P = ParamSpec("P")


def to_async(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await call_or_await(func, *args, **kwargs)

    return wrapper
