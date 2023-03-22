from functools import wraps
from inspect import signature

from propan.utils.context.types import Alias
from propan.utils.context.main import context as global_context


def use_context(func):
    sig = signature(func).parameters

    aliases: dict[str, str] = {}

    for name, param in sig.items():
        if isinstance(param.default, Alias):
            aliases[param.default.name] = name

    function_args = set(sig.keys())
    args_with_aliases_casted = (function_args - set(aliases.values())) | set(aliases.keys())

    @wraps(func)
    def wrapper(*args, **kwargs):
        context = global_context.context

        context_keys = context.keys()
        return func(*args, **kwargs, **{
            aliases.get(k, k): context[k]
            for k in args_with_aliases_casted
            if k in context_keys
        })
    return wrapper
