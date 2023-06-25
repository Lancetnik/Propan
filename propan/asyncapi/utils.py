import json
import sys
from typing import Any, Dict, Optional, Type

from fast_depends._compat import PYDANTIC_V2
from pydantic import BaseModel, Field

if PYDANTIC_V2:
    from pydantic import ConfigDict

    SCHEMA_FIELD = "json_schema_extra"
else:
    # TODO: remove it from with stable PydanticV2
    from pydantic.config import BaseConfig
    from pydantic.config import ConfigDict as CD
    from pydantic.config import get_config

    def ConfigDict(**kwargs: Dict[str, Any]) -> Type[BaseConfig]:  # type: ignore[no-redef]
        return get_config(CD(**kwargs))  # type: ignore

    SCHEMA_FIELD = "schema_extra"


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
    if sys.version_info >= (3, 8):
        from polyfactory.factories.pydantic_factory import ModelFactory

        factory = type(
            f"{model.__name__}_factory", (ModelFactory,), {"__model__": model}
        )

        if PYDANTIC_V2:
            config = getattr(model, "Config", None)
            if config is None:
                config = ConfigDict()
                original = False
            else:
                original = True

            schema_extra = getattr(config, SCHEMA_FIELD, {})
            schema_extra["example"] = schema_extra.get(
                "example",
                json.loads(factory.build().json()),
            )

            if original:
                setattr(config, SCHEMA_FIELD, schema_extra)
            else:
                config[SCHEMA_FIELD] = schema_extra
        else:
            # TODO: remove it from with stable PydanticV2
            schema_extra = model.Config.schema_extra.copy()
            schema_extra["example"] = schema_extra.get(
                "example",
                json.loads(factory.build().json()),
            )
            model = type(
                model.__name__,
                (model,),
                {
                    "Config": type(
                        "Config", (model.Config,), {SCHEMA_FIELD: schema_extra}
                    )
                },
            )
        return model
    else:  # pragma: no cover
        return model
