import json
import sys
from hashlib import md5
from types import MethodType
from typing import Any, Dict, Optional

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock
from uuid import uuid4

from propan import SQSBroker
from propan.brokers.sqs.schema import SQSMessage
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestSQSBroker",
)


def build_message(
    message: SendableMessage,
    queue: str = "",
    headers: Optional[Dict[str, str]] = None,
    delay_seconds: int = 0,  # 0...900
    message_attributes: Optional[Dict[str, Any]] = None,
    message_system_attributes: Optional[Dict[str, Any]] = None,
    # FIFO only
    deduplication_id: Optional[str] = None,
    group_id: Optional[str] = None,
    reply_to: str = "",
) -> Dict[str, Any]:
    params = SQSMessage(
        message=message,
        delay_seconds=delay_seconds,
        headers=headers or {},
        message_attributes=message_attributes or {},
        message_system_attributes=message_system_attributes or {},
        deduplication_id=deduplication_id,
        group_id=group_id,
    ).to_params(reply_to=reply_to)

    body = params.get("MessageBody", "0")
    attributes = params.get("MessageAttributes", {})

    return {
        "Body": body,
        "MD5OfBody": md5(body.encode()).hexdigest(),
        "MD5OfMessageAttributes": md5(json.dumps(attributes).encode()).hexdigest(),
        "MessageAttributes": attributes,
        "MessageId": str(uuid4()),
        "ReceiptHandle": str(uuid4()),
    }


async def publish(
    self: SQSBroker,
    message: SendableMessage,
    queue: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    delay_seconds: int = 0,  # 0...900
    message_attributes: Optional[Dict[str, Any]] = None,
    message_system_attributes: Optional[Dict[str, Any]] = None,
    # FIFO only
    deduplication_id: Optional[str] = None,
    group_id: Optional[str] = None,
    # broker
    reply_to: str = "",
    callback: bool = False,
    callback_timeout: Optional[float] = None,
    raise_timeout: bool = False,
) -> Any:
    incoming = build_message(
        message=message,
        headers=headers,
        delay_seconds=delay_seconds,
        message_attributes=message_attributes,
        message_system_attributes=message_system_attributes,
        deduplication_id=deduplication_id,
        group_id=group_id,
        reply_to=reply_to,
    )

    for handler in self.handlers:  # pragma: no branch
        if queue == handler.queue.name:  # pragma: no branch
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:  # pragma: no branch
                return r


async def delete_message(self: SQSBroker) -> None:
    pass


def TestSQSBroker(broker: SQSBroker) -> SQSBroker:
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock()  # type: ignore
    broker.delete_message = MethodType(delete_message, broker)  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
