from typing import Any


class Singlethon:
    _instanse = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Singlethon":
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse

    @classmethod
    def _drop(cls) -> None:
        cls._instanse = None
