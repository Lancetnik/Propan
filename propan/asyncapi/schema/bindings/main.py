from typing import Optional

from pydantic import BaseModel

from propan.asyncapi.schema.bindings.amqp import ChannelBinding as amqpChannelBinding
from propan.asyncapi.schema.bindings.amqp import (
    OperationBinding as amqpOperationBinding,
)
from propan.asyncapi.schema.bindings.kafka import (
    AsyncAPIKafkaChannelBinding,
    AsyncAPIKafkaOperationBinding,
)
from propan.asyncapi.schema.bindings.nats import (
    AsyncAPINatsChannelBinding,
    AsyncAPINatsOperationBinding,
)
from propan.asyncapi.schema.bindings.redis import (
    AsyncAPIRedisChannelBinding,
    AsyncAPIRedisOperationBinding,
)
from propan.asyncapi.schema.bindings.sqs import (
    AsyncAPISQSChannelBinding,
    AsyncAPISQSOperationBinding,
)


class ServerBinding(BaseModel):
    pass


class ChannelBinding(BaseModel):
    amqp: Optional[amqpChannelBinding] = None
    kafka: Optional[AsyncAPIKafkaChannelBinding] = None
    sqs: Optional[AsyncAPISQSChannelBinding] = None
    nats: Optional[AsyncAPINatsChannelBinding] = None
    redis: Optional[AsyncAPIRedisChannelBinding] = None


class OperationBinding(BaseModel):
    amqp: Optional[amqpOperationBinding] = None
    kafka: Optional[AsyncAPIKafkaOperationBinding] = None
    sqs: Optional[AsyncAPISQSOperationBinding] = None
    nats: Optional[AsyncAPINatsOperationBinding] = None
    redis: Optional[AsyncAPIRedisOperationBinding] = None
