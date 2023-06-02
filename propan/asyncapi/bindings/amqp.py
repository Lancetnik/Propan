from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal


class AsyncAPIAmqpQueue(BaseModel):
    name: str
    durable: bool
    exclusive: bool
    auto_delete: bool = Field(alias="autoDelete")
    vhost: str = "/"

    class Config:
        allow_population_by_field_name = True


class AsyncAPIAmqpExchange(BaseModel):
    name: Optional[str] = None
    type: Literal["default", "direct", "topic", "fanout", "headers"]
    durable: Optional[bool] = None
    auto_delete: Optional[bool] = Field(
        default=None,
        alias="autoDelete",
    )
    vhost: str = "/"

    class Config:
        allow_population_by_field_name = True


class AsyncAPIAmqpChannelBinding(BaseModel):
    is_: Literal["queue", "routingKey"] = Field(..., alias="is")
    version: Optional[str] = Field(
        default=None,
        alias="bindingVersion",
    )
    queue: Optional[AsyncAPIAmqpQueue] = None
    exchange: Optional[AsyncAPIAmqpExchange] = None

    class Config:
        allow_population_by_field_name = True


class AsyncAPIAmqpOperationBinding(BaseModel):
    cc: Optional[str] = None
    ack: bool = True
