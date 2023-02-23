from contextvars import ContextVar
from functools import wraps
from inspect import signature


message = ContextVar("message", default=None)


def use_context(app, func):
    sig = signature(func).parameters
    arg_names = sig.keys()

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = {**app._context, "message": message.get()}
        context_keys = context.keys()
        return func(*args, **kwargs, **{
            k: context[k]
            for k in arg_names
            if k in context_keys
        })
    return wrapper
