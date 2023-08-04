import sys
from datetime import datetime
from types import MethodType
from typing import Any, Dict, Optional

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

from aiokafka.structs import ConsumerRecord

from propan import KafkaBroker
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestKafkaBroker",
)


def build_message(
    message: SendableMessage,
    topic: str,
    partition: Optional[int] = None,
    timestamp_ms: Optional[int] = None,
    key: Optional[bytes] = None,
    headers: Optional[Dict[str, str]] = None,
    *,
    reply_to: str = "",
) -> ConsumerRecord:
    msg, content_type = KafkaBroker._encode_message(message)
    k = key or b""
    headers = {
        "content-type": content_type or "",
        "reply_to": reply_to,
        **(headers or {}),
    }

    return ConsumerRecord(
        value=msg,
        topic=topic,
        partition=partition or 0,
        timestamp=timestamp_ms or int(datetime.now().timestamp()),
        timestamp_type=0,
        key=k,
        serialized_key_size=len(k),
        serialized_value_size=len(msg),
        checksum=sum(msg),
        offset=0,
        headers=[(i, j.encode()) for i, j in headers.items()],
    )


async def publish(
    self: KafkaBroker,
    message: SendableMessage,
    topic: str,
    key: Optional[bytes] = None,
    partition: Optional[int] = None,
    timestamp_ms: Optional[int] = None,
    headers: Optional[Dict[str, str]] = None,
    *,
    reply_to: str = "",
    callback: bool = False,
    callback_timeout: Optional[float] = None,
    raise_timeout: bool = False,
) -> Any:
    incoming = build_message(
        message=message,
        topic=topic,
        key=key,
        partition=partition,
        timestamp_ms=timestamp_ms,
        reply_to=reply_to,
        headers=headers,
    )

    for handler in self.handlers:  # pragma: no branch
        if topic in handler.topics:  # pragma: no branch
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:  # pragma: no branch
                return r


def TestKafkaBroker(broker: KafkaBroker) -> KafkaBroker:
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
