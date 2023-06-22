from typing import List, Optional

from pydantic import BaseModel, Field

from propan.types import AnyDict


class AsyncAPIKafkaChannelBinding(BaseModel):
    topic: List[str]
    partitions: Optional[int] = None
    replicas: Optional[int] = None
    # TODO:
    # topicConfiguration
    version: str = Field(
        default="0.4.0",
        alias="bindingVersion",
    )


class AsyncAPIKafkaOperationBinding(BaseModel):
    group_id: Optional[AnyDict] = Field(
        default=None,
        alias="groupId",
    )
    client_id: Optional[AnyDict] = Field(
        default=None,
        alias="clientId",
    )

    reply_to: Optional[AnyDict] = Field(default=None, alias="replyTo")

    version: str = Field(
        default="0.4.0",
        alias="bindingVersion",
    )
