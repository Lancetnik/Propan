from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NameRequired) and self.name == other.name


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)
