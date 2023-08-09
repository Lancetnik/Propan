from typing import Any, Dict, Optional, Type, overload

from fast_depends.core import CallModel
from pydantic import BaseModel

from propan._compat import get_model_fields, model_schema


def parse_handler_params(call: CallModel[Any, Any], prefix: str = "") -> Dict[str, Any]:
    body = get_model_schema(call.model, prefix=prefix)

    if body is None:
        return {"title": "Payload", "type": "null"}

    return body


@overload
def get_response_schema(call: None, prefix: str = "") -> None:
    ...


@overload
def get_response_schema(call: CallModel[Any, Any], prefix: str = "") -> Dict[str, Any]:
    ...


def get_response_schema(
    call: Optional[CallModel[Any, Any]],
    prefix: str = "",
) -> Optional[Dict[str, Any]]:
    return get_model_schema(
        getattr(
            call, "response_model", None
        ),  # NOTE: FastAPI Dependant object compatibility
        prefix=prefix,
    )


@overload
def get_model_schema(call: None, prefix: str = "") -> None:
    ...


@overload
def get_model_schema(call: Type[BaseModel], prefix: str = "") -> Dict[str, Any]:
    ...


def get_model_schema(
    call: Optional[Type[BaseModel]], prefix: str = ""
) -> Optional[Dict[str, Any]]:
    if call is None:
        return None

    params = get_model_fields(call)
    params_number = len(params)

    if params_number == 0:
        return None

    model = None
    use_original_model = False
    if params_number == 1:
        name, param = tuple(params.items())[0]

        if (
            param.annotation
            and param.annotation != Any
            and issubclass(param.annotation, BaseModel)  # NOTE: 3.7-3.10 compatibility
        ):
            model = param.annotation
            use_original_model = True

    if model is None:
        model = call

    body = model_schema(model)

    if params_number == 1 and not use_original_model:
        param_body = body.get("properties", {})

        param_body = param_body[name]

        param_body["title"] = name

        example = body.get("example", {}).get(name)
        if example is not None:
            param_body["example"] = body.get("example", {}).get(name)

        body = param_body

    if not use_original_model:
        body["title"] = prefix + body["title"].replace("_", " ").title().replace(
            " ", ""
        )

    return body
