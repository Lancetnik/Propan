import json
import sys
from typing import Optional, Type

from fast_depends._compat import PYDANTIC_V2
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


def add_example_to_model(model: Type[BaseModel]) -> Type[BaseModel]:
    if sys.version_info >= (3, 8) and not PYDANTIC_V2:
        from polyfactory.factories.pydantic_factory import ModelFactory

        factory = type(
            f"{model.__name__}_factory", (ModelFactory,), {"__model__": model}
        )

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
    else:  # pragma: no cover
        return model
