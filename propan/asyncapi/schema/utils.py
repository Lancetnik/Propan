from typing import Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field

from propan._compat import TypedDict


class ExternalDocsDict(TypedDict, total=False):
    url: AnyHttpUrl
    description: Optional[str]


class ExternalDocs(BaseModel):
    url: AnyHttpUrl
    description: Optional[str] = None

    model_config = {"extra": "allow"}


class TagDict(TypedDict, total=False):
    name: str
    description: Optional[str]
    externalDocs: Optional[Union[ExternalDocs, ExternalDocsDict]]


class Tag(BaseModel):
    name: str
    description: Optional[str] = None
    externalDocs: Optional[Union[ExternalDocs, ExternalDocsDict]] = None

    model_config = {"extra": "allow"}


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Parameter(BaseModel):
    # TODO
    ...
