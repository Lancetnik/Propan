import importlib.util
import json
from typing import Any, Dict, Type

from fast_depends._compat import PYDANTIC_V2, FieldInfo
from pydantic import BaseModel

from propan.types import AnyDict


def is_installed(package: str) -> bool:
    return importlib.util.find_spec(package)


if PYDANTIC_V2:
    from pydantic import ConfigDict
    from pydantic_core import to_jsonable_python as model_to_jsonable

    SCHEMA_FIELD = "json_schema_extra"

    def dump_json(data: Any) -> str:
        return json.dumps(model_to_jsonable(data))

    def get_model_fileds(model: BaseModel) -> Dict[str, FieldInfo]:
        return model.model_fields

    def model_to_json(model: BaseModel, **kwargs: AnyDict) -> str:
        return model.model_dump_json(**kwargs)

    def model_to_dict(model: BaseModel, **kwargs: AnyDict) -> AnyDict:
        return model.model_dump(**kwargs)

    def model_parse(model: Type[BaseModel], data: bytes, **kwargs: AnyDict) -> AnyDict:
        return model.model_validate_json(data, **kwargs)

    def model_schema(model: Type[BaseModel], **kwargs: AnyDict) -> AnyDict:
        return model.model_json_schema(**kwargs)

else:
    from pydantic.config import BaseConfig
    from pydantic.config import ConfigDict as CD
    from pydantic.config import get_config
    from pydantic.json import pydantic_encoder

    # type: ignore[no-redef]
    def ConfigDict(**kwargs: Dict[str, Any]) -> Type[BaseConfig]:
        return get_config(CD(**kwargs))  # type: ignore

    SCHEMA_FIELD = "schema_extra"

    def dump_json(data: Any) -> str:
        return json.dumps(data, default=pydantic_encoder)

    def get_model_fileds(model: BaseModel) -> Dict[str, FieldInfo]:
        return model.__fields__

    def model_to_json(model: BaseModel, **kwargs: AnyDict) -> str:
        return model.json(**kwargs)

    def model_to_dict(model: BaseModel, **kwargs: AnyDict) -> AnyDict:
        return model.dict(**kwargs)

    def model_parse(model: Type[BaseModel], data: bytes, **kwargs: AnyDict) -> AnyDict:
        return model.parse_raw(data, **kwargs)

    def model_schema(model: Type[BaseModel], **kwargs: AnyDict) -> AnyDict:
        return model.schema(**kwargs)

    def model_to_jsonable(model: BaseModel, **kwargs: AnyDict) -> AnyDict:
        return json.loads(model.json(**kwargs))
