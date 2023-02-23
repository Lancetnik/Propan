from functools import wraps
from inspect import signature, _empty
from typing import Mapping, Callable, Any

from propan.utils.context import Alias


def apply_types(func: Callable) -> Callable:
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())
    annotations = {
        name: param.annotation
        for name, param in sig.items()
        if param.annotation != _empty
    }

    def _cast_type(arg_value: Any, arg_name: str):
        if (arg_type := annotations.get(arg_name)) is not None and \
                not isinstance(arg_type, Alias) and \
                isinstance(arg_value, arg_type) is False:

            if isinstance(arg_value, Mapping):
                arg_value = arg_type(**arg_value)
            else:
                arg_value = arg_type(arg_value)

        return arg_value

    @wraps(func)
    def wrapper(*args, **kwargs):
        kw = {
            arg_name: _cast_type(arg_value, arg_name)
            for arg_name, arg_value in
            (*zip(arg_names, args), *kwargs.items())
        }

        return _cast_type(func(**kw), "return")
    return wrapper
