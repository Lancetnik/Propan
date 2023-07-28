from typing import Optional

from pydantic import BaseModel, Field

from propan.types import AnyDict


class AsyncAPISQSChannelBinding(BaseModel):
    queue: AnyDict
    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )


class AsyncAPISQSOperationBinding(BaseModel):
    reply_to: Optional[AnyDict] = Field(default=None, alias="replyTo")

    version: str = Field(
        default="custom",
        alias="bindingVersion",
    )
