from functools import wraps
from inspect import get_annotations


def apply_types(func):
    types = get_annotations(func)
    ret_type = types.pop('return', None)

    @wraps(func)
    def wrapper(*args, **kwargs):
        kw = {}

        for (arg_name, arg_type), arg in zip(types.items(), args):
            if not isinstance(arg, arg_type):
                arg = arg_type(arg)
            kw[arg_name] = arg
        
        for arg_name, arg in kwargs.items():
            arg_type = types[arg_name]
            if not isinstance(arg, arg_type):
                arg = arg_type(arg)
            kw[arg_name] = arg
        
        if ret_type is None:
            return func(**kw)
        else:
            return ret_type(func(**kw))
    return wrapper
