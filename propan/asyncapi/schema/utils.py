from typing import Optional, TypedDict, Union

from pydantic import AnyHttpUrl, BaseModel, Field


class ExternalDocsDict(TypedDict, total=False):
    url: AnyHttpUrl
    description: Optional[str]


class ExternalDocs(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None


class TagDict(TypedDict, total=False):
    name: str
    description: Optional[str]
    externalDocs: Optional[Union[ExternalDocs, ExternalDocsDict]]


class Tag(BaseModel):
    name: str
    description: Optional[str] = None
    externalDocs: Optional[Union[ExternalDocs, ExternalDocsDict]] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Parameter(BaseModel):
    # TODO
    ...
