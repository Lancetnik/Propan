import sys
from types import MethodType
from typing import Any, Dict, Optional

from nats.aio.msg import Msg

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

from propan import NatsBroker
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestNatsBroker",
)


def build_message(
    message: SendableMessage,
    subject: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
) -> Msg:
    msg, content_type = NatsBroker._encode_message(message)
    return Msg(
        _client=None,  # type: ignore
        subject=subject,
        reply=reply_to,
        data=msg,
        headers={
            **(headers or {}),
            "content-type": content_type or "",
        },
    )


async def publish(
    self: NatsBroker,
    message: SendableMessage,
    subject: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    incoming = build_message(
        message=message,
        subject=subject,
        reply_to=reply_to,
        headers=headers,
    )

    for handler in self.handlers:  # pragma: no branch
        if subject == handler.subject:  # pragma: no branch
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:  # pragma: no branch
                return r


def TestNatsBroker(broker: NatsBroker) -> NatsBroker:
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
