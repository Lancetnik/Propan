from inspect import isclass
from typing import Any, Dict, Optional, Sequence, Type, overload

from fast_depends.core import CallModel
from pydantic import BaseModel

from propan._compat import get_model_fields, model_schema
from propan.asyncapi.utils import to_camelcase


def parse_handler_params(call: CallModel[Any, Any], prefix: str = "") -> Dict[str, Any]:
    body = get_model_schema(
        call.model, prefix=prefix, exclude=tuple(call.custom_fields.keys())
    )
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
def get_model_schema(
    call: None,
    prefix: str = "",
    exclude: Sequence[str] = (),
) -> None:
    ...


@overload
def get_model_schema(
    call: Type[BaseModel],
    prefix: str = "",
    exclude: Sequence[str] = (),
) -> Dict[str, Any]:
    ...


def get_model_schema(
    call: Optional[Type[BaseModel]],
    prefix: str = "",
    exclude: Sequence[str] = (),
) -> Optional[Dict[str, Any]]:
    if call is None:
        return None

    params = {k: v for k, v in get_model_fields(call).items() if k not in exclude}
    params_number = len(params)

    if params_number == 0:
        return None

    model = None
    use_original_model = False
    if params_number == 1:
        name, param = tuple(params.items())[0]

        if (
            param.annotation
            and isclass(param.annotation)
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

    camel_body = to_camelcase(body["title"])
    if not use_original_model:
        if prefix != camel_body:
            body["title"] = f"{prefix}{camel_body}Payload"
        else:
            body["title"] = f"{camel_body}Payload"

    return body
