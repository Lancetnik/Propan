from typing import Optional

from pydantic import BaseModel

from propan.asyncapi.bindings.amqp import (
    AsyncAPIAmqpChannelBinding,
    AsyncAPIAmqpOperationBinding,
)
from propan.asyncapi.bindings.kafka import (
    AsyncAPIKafkaChannelBinding,
    AsyncAPIKafkaOperationBinding,
)
from propan.asyncapi.bindings.nats import (
    AsyncAPINatsChannelBinding,
    AsyncAPINatsOperationBinding,
)
from propan.asyncapi.bindings.redis import (
    AsyncAPIRedisChannelBinding,
    AsyncAPIRedisOperationBinding,
)
from propan.asyncapi.bindings.sqs import (
    AsyncAPISQSChannelBinding,
    AsyncAPISQSOperationBinding,
)


class AsyncAPIChannelBinding(BaseModel):
    amqp: Optional[AsyncAPIAmqpChannelBinding] = None
    kafka: Optional[AsyncAPIKafkaChannelBinding] = None
    sqs: Optional[AsyncAPISQSChannelBinding] = None
    nats: Optional[AsyncAPINatsChannelBinding] = None
    redis: Optional[AsyncAPIRedisChannelBinding] = None


class AsyncAPIOperationBinding(BaseModel):
    amqp: Optional[AsyncAPIAmqpOperationBinding] = None
    kafka: Optional[AsyncAPIKafkaOperationBinding] = None
    sqs: Optional[AsyncAPISQSOperationBinding] = None
    nats: Optional[AsyncAPINatsOperationBinding] = None
    redis: Optional[AsyncAPIRedisOperationBinding] = None
