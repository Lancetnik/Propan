from typing import Optional, Type

from pydantic import BaseModel, Field

from propan._compat import update_model_example


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


def add_example_to_model(model: Type[BaseModel]) -> Type[BaseModel]:
    return update_model_example(model)
