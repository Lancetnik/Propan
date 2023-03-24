from functools import wraps
from inspect import signature, _empty
from typing import Mapping, Callable, Any

from propan.utils.context.types import Alias, Depends


NOT_CAST = (Alias, Depends)


def apply_types(func: Callable) -> Callable:
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())
    annotations = {
        name: param.annotation
        for name, param in sig.items()
        if param.annotation != _empty and type(param.default) not in NOT_CAST
    }

    def _cast_type(arg_value: Any, arg_name: str):
        if (arg_type := annotations.get(arg_name)) is not None and \
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
