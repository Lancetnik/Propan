from functools import wraps


def apply_types(func):
    types = func.__annotations__

    @wraps(func)
    def wrapper(*args, **kwargs):
        args_position = 0
        kw = {}
        for arg, arg_type in types.items():
            kw[arg] = kwargs.pop(arg, None)
            if kw[arg] is None:
                kw[arg] = args[args_position]
                args_position += 1
            if not isinstance(kw[arg], arg_type):
                kw[arg] = arg_type(kw[arg])
        return func(**kw)
    return wrapper
