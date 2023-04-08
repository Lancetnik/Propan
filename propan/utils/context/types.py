from propan.types import DecoratedCallable


class Alias:
    def __init__(self, real_name: str):
        self.name = real_name


class Depends:
    def __init__(self, func: DecoratedCallable):
        self.func = func

    def __repr__(self) -> str:
        attr = getattr(self.func, "__name__", type(self.func).__name__)
        return f"{self.__class__.__name__}({attr})"
