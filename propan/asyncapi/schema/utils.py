from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class ExternalDocs(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None


class Tag(BaseModel):
    name: str
    description: str = ""
    externalDocs: Optional[ExternalDocs] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Parameter(BaseModel):
    # TODO
    ...
