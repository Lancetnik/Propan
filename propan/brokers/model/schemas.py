import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Sequence, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel, Field, Json
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import TypeAlias, assert_never

from propan.types import AnyDict, DecodedMessage, DecoratedCallable, SendableMessage

ContentType: TypeAlias = str


@dataclass
class BaseHandler:
    callback: DecoratedCallable


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
class PropanMessage:
    body: bytes
    raw_message: Any
    content_type: Optional[str] = None
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))
