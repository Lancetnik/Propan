from functools import wraps
from typing import Callable, TypeVar

from fast_depends.injector import run_async as call_or_await
from propan.types import P

T = TypeVar("T")


def to_async(func: Callable[[P], T]) -> Callable[[P], T]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await call_or_await(func, *args, **kwargs)

    return wrapper
