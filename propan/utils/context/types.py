from typing import Any

from fast_depends.library import CustomField
from propan.utils.context import context


class Context(CustomField):
    def __init__(
        self, real_name: str = "", *, cast: bool = False, required: bool = True
    ):
        self.name = real_name
        super().__init__(cast=cast, required=required)

    def use(self, **kwargs):
        name = self.name or self.param_name
        return {**kwargs, self.param_name: resolve_context(name)}


def resolve_context(argument: str) -> Any:
    keys = argument.split(".")

    v = context.context.get(keys[0])
    for i in keys[1:]:
        v = getattr(v, i, None)
        if v is None:
            return v

    return v
