from inspect import _empty
from typing import Any

from fast_depends.library import CustomField

from propan.types import AnyDict
from propan.utils.context import context


class Context(CustomField):
    def __init__(
        self, real_name: str = "", *, cast: bool = False, default: Any = _empty
    ):
        self.name = real_name
        self.default = default
        super().__init__(cast=cast, required=(default is _empty))

    def use(self, **kwargs: AnyDict) -> AnyDict:
        name = self.name or self.param_name
        default = None if self.default is _empty else self.default
        return {**kwargs, self.param_name: resolve_context(name) or default}


def resolve_context(argument: str) -> Any:
    keys = argument.split(".")

    v = context.context.get(keys[0])
    for i in keys[1:]:
        v = getattr(v, i, None)
        if v is None:
            return v

    return v
