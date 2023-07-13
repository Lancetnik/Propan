from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, Tuple, Type, TypeVar, Union
from uuid import uuid4

from fast_depends.core import CallModel
from pydantic import BaseModel, Field, Json, create_model
from pydantic.dataclasses import dataclass as pydantic_dataclass

from propan._compat import get_model_fileds, model_schema, update_model_example
from propan.asyncapi.channels import AsyncAPIChannel
from propan.types import AnyDict, DecodedMessage, DecoratedCallable


@dataclass
class BaseHandler:
    callback: DecoratedCallable
    dependant: CallModel
    _description: str

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: CallModel,
        _description: str = "",
    ):
        self.callback = callback
        self.dependant = dependant
        self._description = _description

    @abstractmethod
    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        raise NotImplementedError()

    @property
    def title(self) -> str:
        return self.callback.__name__.replace("_", " ").title().replace(" ", "")

    @property
    def description(self) -> Optional[str]:
        return self._description or self.callback.__doc__

    def get_message_object(self) -> Tuple[str, AnyDict, Optional[AnyDict]]:
        import jsonref  # hide it there to remove docs dependencies from main package

        dependant = self.dependant

        if getattr(dependant, "response_model", None) is not None:
            response_model: Type[BaseModel] = dependant.response_model
            return_field = list(get_model_fileds(response_model).values())[0]

            if (
                return_field.annotation != Any  # NOTE: 3.7-3.10 compatibility
                and issubclass(return_field.annotation, BaseModel)
            ):
                response_model = update_model_example(return_field.annotation)

                return_info = jsonref.replace_refs(
                    model_schema(response_model), jsonschema=True, proxies=False
                )
                return_info["examples"] = [return_info.pop("example", None)]

            else:
                response_model = update_model_example(response_model)
                response_field_name = "response"

                raw = jsonref.replace_refs(
                    model_schema(response_model),
                    jsonschema=True,
                    proxies=False,
                )

                return_info = raw.get("properties", {}).get(response_field_name)
                return_info["examples"] = [
                    raw.pop("example", {}).get(response_field_name)
                ]
                return_info["title"] = f"{self.title}Reply"
        else:
            return_info = None

        payload_title = f"{self.title}Payload"
        params = dependant.flat_params
        params_number = len(params)

        use_original_model = False
        if params_number == 0:
            model = None

        elif params_number == 1:
            name, param = list(params.items())[0]
            info = getattr(param, "field_info", param)

            if param.annotation != Any and issubclass(  # NOTE: 3.7-3.10 compatibility
                param.annotation, BaseModel
            ):
                model = param.annotation
                use_original_model = True

            else:
                model = create_model(  # type: ignore
                    info.title or payload_title,
                    **{name: (param.annotation, info)},
                )

        else:
            model = create_model(  # type: ignore
                payload_title,
                **{
                    i: (j.annotation, getattr(j, "field_info", j))
                    for i, j in params.items()
                },
            )

        body: AnyDict
        if model is None:
            body = {"title": payload_title, "type": "null"}
        else:
            model = update_model_example(model)
            body = jsonref.replace_refs(
                model_schema(model), jsonschema=True, proxies=False
            )

        body.pop("definitions", None)
        if return_info is not None:
            return_info.pop("definitions", None)

        if params_number == 1 and not use_original_model:
            param_body: AnyDict = body.get("properties", {})
            key = list(param_body.keys())[0]
            param_body = param_body[key]
            param_body.update(
                {
                    "example": body.get("example", {}).get(key),
                    "title": body.get("title", param_body.get("title")),
                }
            )
            param_body["example"] = body.get("example", {}).get(key)
            body = param_body

        return f"{self.title}Message", body, return_info


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __eq__(self, __value: Optional["NameRequired"]) -> bool:
        return __value and self.name == __value.name

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]


Msg = TypeVar("Msg")


@pydantic_dataclass
class PropanMessage(Generic[Msg]):
    raw_message: Msg
    body: Union[bytes, Any]
    content_type: Optional[str] = None
    reply_to: str = ""
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    decoded_body: Optional[DecodedMessage] = None
