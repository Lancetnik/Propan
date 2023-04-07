from typing import Any, Callable


class Alias:
    def __init__(self, real_name: str):
        self.name = real_name


class Depends:
    def __init__(self, func: Callable[..., Any]):
        self.func = func
