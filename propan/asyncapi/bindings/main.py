from typing import Optional

from pydantic import BaseModel

from propan.asyncapi.bindings.amqp import (
    AsyncAPIAmqpChannelBinding,
    AsyncAPIAmqpOperationBinding,
)


class AsyncAPIChannelBinding(BaseModel):
    amqp: Optional[AsyncAPIAmqpChannelBinding] = None


class AsyncAPIOperationBinding(BaseModel):
    amqp: Optional[AsyncAPIAmqpOperationBinding] = None
