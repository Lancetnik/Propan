from typing import Optional

from pydantic import BaseModel, Field


class AsyncAPIExternalDocs(BaseModel):
    url: str = ""
    description: str = ""


class AsyncAPITag(BaseModel):
    name: str
    description: str = ""
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )

    class Config:
        allow_population_by_field_name = True
