import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer

from propan.asyncapi.bindings import (
    AsyncAPIChannelBinding,
    AsyncAPIOperationBinding,
    kafka,
)
from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.message import AsyncAPICorrelationId, AsyncAPIMessage
from propan.asyncapi.subscription import AsyncAPISubscription
from propan.brokers._model.schemas import BaseHandler
from propan.types import AnyDict


@dataclass
class Handler(BaseHandler):
    topics: List[str]
    group_id: Optional[str] = None

    consumer: Optional[AIOKafkaConsumer] = None
    task: Optional["asyncio.Task[Any]"] = None
    consumer_kwargs: AnyDict = field(default_factory=dict)

    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        message_title, body, reply_to = self.get_message_object()

        if reply_to:
            kafka_kwargs = {"replyTo": reply_to}
        else:
            kafka_kwargs = {}

        if self.group_id is not None:
            kafka_kwargs["groupId"] = {"type": "string", "enum": [self.group_id]}

        if kafka_kwargs:
            operation_binding = AsyncAPIOperationBinding(
                kafka=kafka.AsyncAPIKafkaOperationBinding(**kafka_kwargs)  # type: ignore
            )
        else:
            operation_binding = None

        return {
            self.title: AsyncAPIChannel(
                subscribe=AsyncAPISubscription(
                    description=self.description,
                    bindings=operation_binding,
                    message=AsyncAPIMessage(
                        title=message_title,
                        payload=body,
                        correlationId=AsyncAPICorrelationId(
                            location="$message.header#/correlation_id"
                        ),
                    ),
                ),
                bindings=AsyncAPIChannelBinding(
                    kafka=kafka.AsyncAPIKafkaChannelBinding(
                        topic=self.topics,
                    )
                ),
            ),
        }
