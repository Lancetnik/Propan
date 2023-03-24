from inspect import signature, iscoroutinefunction

from typing import Any


async def call_or_await(func, *args, **kwargs) -> Any:
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


def remove_useless_arguments(func, *args, **kwargs) -> dict:
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())
    
    return {
        arg_name: arg_value
        for arg_name, arg_value in
        (*zip(arg_names, args), *kwargs.items())
        if arg_name in arg_names
    }
