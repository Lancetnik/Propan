from functools import partial
from inspect import iscoroutinefunction, signature
from typing import Any, Dict

import anyio
from propan.types import DecoratedCallable


async def call_or_await(func: DecoratedCallable, *args: Any, **kwargs: Any) -> Any:
    if iscoroutinefunction(func) is True:
        return await func(*args, **kwargs)
    else:
        if kwargs:  # pragma: no cover
            func = partial(func, **kwargs)
        return await anyio.to_thread.run_sync(func, *args)


def remove_useless_arguments(
    func: DecoratedCallable, *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())

    return {
        arg_name: arg_value
        for arg_name, arg_value in (*zip(arg_names, args), *kwargs.items())
        if arg_name in arg_names
    }
