import re
import sys
from types import MethodType
from typing import Any, Dict, Optional, Union

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

from typing_extensions import TypeAlias

from propan._compat import model_to_json
from propan.brokers.redis.redis_broker import RedisBroker
from propan.brokers.redis.schemas import RedisMessage
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestRedisBroker",
)

Msg: TypeAlias = Dict[str, Union[bytes, str, None]]


def build_message(
    message: SendableMessage,
    channel: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
) -> Msg:
    msg, content_type = RedisBroker._encode_message(message)
    return {
        "type": "message",
        "pattern": None,
        "channel": channel.encode(),
        "data": model_to_json(
            RedisMessage(
                data=msg,
                headers={
                    "content-type": content_type or "",
                    **(headers or {}),
                },
                reply_to=reply_to,
            )
        ).encode(),
    }


async def publish(
    self: RedisBroker,
    message: SendableMessage,
    channel: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    incoming = build_message(
        message=message,
        channel=channel,
        reply_to=reply_to,
        headers=headers,
    )

    for handler in self.handlers:  # pragma: no branch
        if (
            not handler.pattern and handler.channel == channel
        ) or (  # pragma: no branch
            handler.pattern and re.match(handler.channel, channel)
        ):
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:  # pragma: no branch
                return r


def TestRedisBroker(broker: RedisBroker) -> RedisBroker:
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
