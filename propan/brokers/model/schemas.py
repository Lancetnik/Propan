from typing import Optional

from pydantic import BaseModel, Field


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)

    def __hash__(self):
        return hash(self.json())


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
