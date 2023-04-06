from typing import Optional

from pydantic import BaseModel, Field


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)

    def __eq__(self, other: "NameRequired") -> bool:
        return self.name == other.name


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
