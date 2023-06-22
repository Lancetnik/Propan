from dataclasses import dataclass
from typing import Dict, Optional, Sequence

from fast_depends.core import CallModel
from nats.aio.subscription import Subscription
from nats.js.api import DEFAULT_PREFIX
from pydantic import BaseModel

from propan.asyncapi.bindings import (
    AsyncAPIChannelBinding,
    AsyncAPIOperationBinding,
    nats,
)
from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.message import AsyncAPIMessage
from propan.asyncapi.subscription import AsyncAPISubscription
from propan.brokers._model.schemas import BaseHandler
from propan.types import DecoratedCallable


@dataclass
class Handler(BaseHandler):
    subject: str
    queue: str = ""

    subscription: Optional[Subscription] = None

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: CallModel,
        subject: str,
        queue: str = "",
        subscription: Optional[Subscription] = None,
        _description: str = "",
    ):
        self.callback = callback
        self.dependant = dependant
        self._description = _description
        self.subject = subject
        self.queue = queue
        self.subscription = subscription

    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        message_title, body, reply_to = self.get_message_object()

        return {
            self.title: AsyncAPIChannel(
                subscribe=AsyncAPISubscription(
                    description=self.description,
                    bindings=AsyncAPIOperationBinding(
                        nats=nats.AsyncAPINatsOperationBinding(
                            replyTo=reply_to,
                        ),
                    ),
                    message=AsyncAPIMessage(
                        title=message_title,
                        payload=body,
                    ),
                ),
                bindings=AsyncAPIChannelBinding(
                    nats=nats.AsyncAPINatsChannelBinding(
                        subject=self.subject,
                        queue=self.queue or None,
                    )
                ),
            ),
        }


class JetStream(BaseModel):
    prefix: str = DEFAULT_PREFIX
    domain: Optional[str] = None
    timeout: float = 5

    subjects: Sequence[str] = []
