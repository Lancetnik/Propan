from typing import Any, Optional

from pydantic import BaseModel, Field


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NameRequired):
            raise ValueError(f"{other} is not NameRequired type")
        return self.name == other.name


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)
