from inspect import isawaitable, signature
from typing import Any, Callable, Dict


async def call_or_await(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    f = func(*args, **kwargs)
    if isawaitable(f):
        f = await f
    return f


def remove_useless_arguments(
    func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())

    return {
        arg_name: arg_value
        for arg_name, arg_value in (*zip(arg_names, args), *kwargs.items())
        if arg_name in arg_names
    }
