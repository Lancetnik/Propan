import json
from enum import Enum
from typing import Any, Optional, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from typing_extensions import TypeAlias

from propan.types import AnyDict, DecodedMessage, SendableMessage

ContentType: TypeAlias = str


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"


class NameRequired(BaseModel):
    name: Optional[str] = Field(...)

    def __init__(self, name: str, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NameRequired) and self.name == other.name


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

        if isinstance(m, dict):
            return json.dumps(m).encode(), ContentTypes.json.value

        if isinstance(m, str):
            return m.encode(), ContentTypes.text.value

        return m, None


@dataclass
class PropanMessage:
    body: bytes
    raw_message: Any
    content_type: str
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))
