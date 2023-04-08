from functools import wraps
from inspect import iscoroutinefunction, signature
from typing import Any, Callable, Dict, List, TypeVar, Tuple

from propan.utils.context.main import context as global_context
from propan.utils.context.types import Alias, Depends
from propan.utils.functions import call_or_await, remove_useless_arguments

FuncArgName = TypeVar("FuncArgName", bound=str)
AliasStr = TypeVar("AliasStr", bound=str)


def use_context(func: Callable[..., Any]) -> Callable[..., Any]:
    sig = signature(func).parameters

    aliases: Dict[AliasStr, FuncArgName] = {}
    dependencies: Dict[FuncArgName, Callable[..., Any]] = {}

    for name, param in sig.items():
        annotated_attr = getattr(param.annotation, "__metadata__", None)
        if annotated_attr is not None:
            attr = annotated_attr[0]
        else:
            attr = param.default

        if isinstance(attr, Alias):
            aliases[attr.name] = name
        elif isinstance(attr, Depends):
            dependencies[name] = attr.func

    func_args_with_aliases_casted = (set(sig.keys()) - set(aliases.values())) | set(
        aliases.keys()
    )

    def _cast_context(*args: Any, **kwargs: Any) -> Tuple[Any, Any]:
        context = global_context.context

        context_keys = context.keys()

        for k in func_args_with_aliases_casted:
            keys = k.split(".")

            func_argument_name = aliases.get(k, k)
            if keys[0] in kwargs.keys():
                func_argument_value = _get_context_by_key(kwargs, keys)
            elif keys[0] in context_keys:
                func_argument_value = _get_context_by_key(context, keys)
            else:
                func_argument_value = None
            kwargs[func_argument_name] = func_argument_value

        return args, kwargs

    if iscoroutinefunction(func) is True:

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = _cast_context(*args, **kwargs)
            for k, f in dependencies.items():
                kw = remove_useless_arguments(f, *args, **kwargs)
                kwargs[k] = await call_or_await(f, **kw)
            return await func(*args, **kwargs)

    else:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = _cast_context(*args, **kwargs)
            for k, f in dependencies.items():
                if iscoroutinefunction(f) is True:
                    raise ValueError("You can't use async Depends with sync function")

                kw = remove_useless_arguments(f, *args, **kwargs)
                kwargs[k] = f(**kw)
            return func(*args, **kwargs)

    return wrapper


def _get_context_by_key(context: Dict[str, Any], keys: List[str]) -> Any:
    v = context.get(keys[0])
    for i in keys[1:]:
        v = getattr(v, i, None)
        if v is None:
            return v
    return v
