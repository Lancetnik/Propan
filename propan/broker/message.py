from abc import abstractmethod
from typing import Any, Generic, Optional, Union
from uuid import uuid4

from pydantic import Field
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing_extensions import TypeVar

from propan.types import AnyDict, DecodedMessage

Msg = TypeVar("Msg")


@pydantic_dataclass
class PropanMessage(Generic[Msg]):
    raw_message: Msg

    body: Union[bytes, Any]
    decoded_body: Optional[DecodedMessage] = None

    content_type: Optional[str] = None
    reply_to: str = ""
    headers: AnyDict = Field(default_factory=dict)
    message_id: str = Field(default_factory=lambda: str(uuid4()))  # pragma: no cover
    correlation_id: str = Field(
        default_factory=lambda: str(uuid4())
    )  # pragma: no cover

    processed: bool = False

    @abstractmethod
    def ack(self, **kwargs: AnyDict) -> None:
        raise NotImplementedError()

    @abstractmethod
    def nack(self, **kwargs: AnyDict) -> None:
        raise NotImplementedError()

    @abstractmethod
    def reject(self, **kwargs: AnyDict) -> None:
        raise NotImplementedError()
