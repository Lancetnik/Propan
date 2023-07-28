from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class AsyncAPIExternalDocs(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None


class AsyncAPITag(BaseModel):
    name: str
    description: str = ""
    externalDocs: Optional[AsyncAPIExternalDocs] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Parameter(BaseModel):
    # TODO
    ...
