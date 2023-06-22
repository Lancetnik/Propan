from typing import Optional

from pydantic import BaseModel, Field

from propan.types import AnyDict


class AsyncAPINatsChannelBinding(BaseModel):
    subject: str
    queue: Optional[str] = None
    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )


class AsyncAPINatsOperationBinding(BaseModel):
    reply_to: Optional[AnyDict] = Field(default=None, alias="replyTo")
    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )
