import json
from typing import Optional, Type

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


def add_example_to_model(model: Type[BaseModel]) -> Type[BaseModel]:
    from polyfactory.factories.pydantic_factory import (
        ModelFactory,
    )  # mv it to hide from main dependencies

    factory = type(f"{model.__name__}_factory", (ModelFactory,), {"__model__": model})

    return type(
        model.__name__,
        (model,),
        {
            "Config": type(
                "Config",
                (model.Config,),
                {
                    "schema_extra": {
                        "example": json.loads(factory.build().json()),
                    },
                },
            )
        },
    )
