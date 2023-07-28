from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

from propan.types import AnyDict


class AsyncAPIRedisChannelBinding(BaseModel):
    channel: str
    method: Literal["ssubscribe", "psubscribe", "subscribe"] = "subscribe"
    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )


class AsyncAPIRedisOperationBinding(BaseModel):
    reply_to: Optional[AnyDict] = Field(default=None, alias="replyTo")
    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )
