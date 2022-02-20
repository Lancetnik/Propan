from functools import wraps
from inspect import getfullargspec


def apply_types(func):
    f_info = getfullargspec(func)
    arg_names = f_info.args
    annotations = f_info.annotations

    def _cast_type(arg_value, arg_name):
        if (arg_type := annotations.get(arg_name)) is not None and \
                isinstance(arg_value, arg_type) is False:
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
