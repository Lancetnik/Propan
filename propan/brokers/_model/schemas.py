import json
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from inspect import _empty
from typing import Any, Dict, Generic, Optional, Sequence, Tuple, TypeVar, Union
from uuid import uuid4

from fast_depends.model import Dependant
from pydantic import BaseModel, Field, Json, create_model
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import TypeAlias, assert_never

from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.utils import add_example_to_model
from propan.types import AnyDict, DecodedMessage, DecoratedCallable, SendableMessage

ContentType: TypeAlias = str

Msg = TypeVar("Msg")


@dataclass
class BaseHandler:
    callback: DecoratedCallable
    dependant: Dependant
    _description: str

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: Dependant,
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

        if getattr(dependant, "return_field", None) is not None:
            return_field = dependant.return_field

            if issubclass(return_field.type_, BaseModel):
                return_model = return_field.type_
                if not return_model.Config.schema_extra.get("example"):
                    return_model = add_example_to_model(return_model)
                return_info = jsonref.replace_refs(
                    return_model.schema(), jsonschema=True, proxies=False
                )
                return_info["examples"] = [return_info.pop("example", [])]

            else:
                return_model = create_model(  # type: ignore
                    f"{self.title}Reply",
                    **{return_field.name: (return_field.annotation, ...)},
                )
                return_model = add_example_to_model(return_model)
                return_info = jsonref.replace_refs(
                    return_model.schema(), jsonschema=True, proxies=False
                )
                return_info.pop("required")
                return_info.update(
                    {
                        "type": return_info.pop("properties", {})
                        .get(return_field.name, {})
                        .get("type"),
                        "examples": [
                            return_info.pop("example", {}).get(return_field.name)
                        ],
                    }
                )

        else:
            return_info = None

        payload_title = f"{self.title}Payload"
        params = dependant.flat_params
        params_number = len(params)

        gen_examples: bool
        use_original_model = False
        if params_number == 0:
            model = None

        elif params_number == 1:
            param = params[0]

            if issubclass(param.annotation, BaseModel):
                model = param.annotation
                gen_examples = model.Config.schema_extra.get("example") is None
                use_original_model = True

            else:
                is_pydantic = param.field_info.default is not _empty
                model = create_model(  # type: ignore
                    param.field_info.title or payload_title,
                    **{
                        param.name: (
                            param.annotation,
                            param.field_info if is_pydantic else ...,
                        )
                    },
                )
                gen_examples = True

        else:
            model = create_model(  # type: ignore
                payload_title,
                **{
                    p.name: (
                        p.annotation,
                        ... if p.field_info.default is _empty else p.field_info,
                    )
                    for p in params
                },
            )
            gen_examples = True

        body: AnyDict
        if model is None:
            body = {"title": payload_title, "type": "null"}
        else:
            if gen_examples is True:
                model = add_example_to_model(model)
            body = jsonref.replace_refs(model.schema(), jsonschema=True, proxies=False)

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


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class Queue(NameRequired):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)


class SendableModel(BaseModel):
    message: DecodedMessage

    @classmethod
    def to_send(cls, msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
        if msg is None:
            return b"", None

        if isinstance(msg, bytes):
            return msg, None

        m = cls(message=msg).message  # type: ignore

        if isinstance(m, str):
            return m.encode(), ContentTypes.text.value

        if isinstance(m, (Dict, Sequence)):
            return json.dumps(m).encode(), ContentTypes.json.value

        assert_never()  # pragma: no cover


class RawDecoced(BaseModel):
    message: Union[Json[Any], str]


@pydantic_dataclass
class PropanMessage(Generic[Msg]):
    body: Union[bytes, Any]
    raw_message: Msg
    content_type: Optional[str] = None
    reply_to: str = ""
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    decoded_body: Optional[DecodedMessage] = None
