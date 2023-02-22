from functools import wraps
from inspect import signature


def use_context(app, func):
    sig = signature(func).parameters
    arg_names = sig.keys()

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs, **{
            k: v
            for k, v in app._context.items()
            if k in arg_names
        })
    return wrapper
