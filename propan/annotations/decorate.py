import json

from functools import wraps
from typing import Mapping
from inspect import signature, _empty


def apply_types(func):
    sig = signature(func).parameters
    arg_names = tuple(sig.keys())
    annotations = {
        name: param.annotation
        for name, param in sig.items()
        if param.annotation != _empty
    }

    def _cast_type(arg_value, arg_name):
        if (arg_type := annotations.get(arg_name)) is not None and \
                isinstance(arg_value, arg_type) is False:

            if isinstance(arg_value, Mapping):
                arg_value = arg_type(**arg_value)
            else:
                arg_value = arg_type(arg_value)

        return arg_value

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(arg_names) > 1:
            kwargs = json.loads(args[0])
            args = []

        kw = {
            arg_name: _cast_type(arg_value, arg_name)
            for arg_name, arg_value in
            (*zip(arg_names, args), *kwargs.items())
        }

        return _cast_type(func(**kw), "return")
    return wrapper
