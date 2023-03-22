import inspect
from typing import Any


async def call_or_await(func, *args, **kwargs) -> Any:
    f = func(*args, **kwargs)
    if inspect.isawaitable(f):
        f = await f
    return f
