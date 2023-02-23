from contextvars import ContextVar
from functools import wraps
from inspect import signature

from .types import Alias


global_context = {}

message = ContextVar("message", default=None)


def use_context(func):
    sig = signature(func).parameters

    aliases = {
        param.default.name: name
        for name, param in sig.items()
        if isinstance(param.default, Alias)
    }

    arg_names = (set(sig.keys()) - set(aliases.values())) | set(aliases.keys())

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = {**global_context, "message": message.get()}
        context_keys = context.keys()
        return func(*args, **kwargs, **{
            aliases.get(k, k): context[k]
            for k in arg_names
            if k in context_keys
        })
    return wrapper
