import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fast_depends.core import CallModel
from pydantic import BaseModel, Field
from redis.asyncio.client import PubSub

from propan.asyncapi.bindings import (
    AsyncAPIChannelBinding,
    AsyncAPIOperationBinding,
    redis,
)
from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.message import AsyncAPIMessage
from propan.asyncapi.subscription import AsyncAPISubscription
from propan.brokers._model.schemas import BaseHandler
from propan.types import DecoratedCallable


@dataclass
class Handler(BaseHandler):
    channel: str
    pattern: bool = False

    task: Optional["asyncio.Task[Any]"] = None
    subscription: Optional[PubSub] = None

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: CallModel,
        channel: str,
        pattern: bool = False,
        task: Optional["asyncio.Task[Any]"] = None,
        subscription: Optional[PubSub] = None,
        _description: str = "",
    ):
        self.callback = callback
        self.dependant = dependant
        self._description = _description
        self.channel = channel
        self.pattern = pattern
        self.task = task
        self.subscription = subscription

    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        message_title, body, reply_to = self.get_message_object()

        return {
            self.title: AsyncAPIChannel(
                subscribe=AsyncAPISubscription(
                    description=self.description,
                    bindings=AsyncAPIOperationBinding(
                        redis=redis.AsyncAPIRedisOperationBinding(
                            replyTo=reply_to,
                        ),
                    ),
                    message=AsyncAPIMessage(
                        title=message_title,
                        payload=body,
                    ),
                ),
                bindings=AsyncAPIChannelBinding(
                    redis=redis.AsyncAPIRedisChannelBinding(
                        channel=self.channel,
                        method="psubscribe" if self.pattern else "subscribe",
                    )
                ),
            ),
        }


class RedisMessage(BaseModel):
    data: bytes
    headers: Dict[str, str] = Field(default_factory=dict)
    reply_to: str = ""
