from fast_depends.library import CustomField

from propan.types import AnyDict


class NoCast(CustomField):  # type: ignore
    def __init__(self) -> None:
        super().__init__(cast=False)

    def use(self, **kwargs: AnyDict) -> AnyDict:
        return kwargs
