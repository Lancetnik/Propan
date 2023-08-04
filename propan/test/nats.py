import sys
from types import MethodType
from typing import Any, Dict, Optional, Union

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock
from uuid import uuid4

from nats.aio.msg import Msg

from propan import NatsBroker
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestNatsBroker",
)


class PatchedMessage(Msg):
    async def ack(self) -> None:
        pass

    async def ack_sync(self, timeout: float = 1) -> None:
        pass

    async def nak(self, delay: Union[int, float, None] = None) -> None:
        pass

    async def term(self) -> None:
        pass

    async def in_progress(self) -> None:
        pass


def build_message(
    message: SendableMessage,
    subject: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
) -> PatchedMessage:
    msg, content_type = NatsBroker._encode_message(message)
    return PatchedMessage(
        _client=None,  # type: ignore
        subject=subject,
        reply=reply_to or str(uuid4()),
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
    broker._raw_connection = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
