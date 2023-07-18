import json
from typing import Any, Optional, Tuple

from propan._compat import dump_json
from propan.broker.message import PropanMessage
from propan.constants import ContentType, ContentTypes
from propan.types import DecodedMessage, SendableMessage


def decode_message(message: PropanMessage[Any]) -> DecodedMessage:
    body = message.body
    m: DecodedMessage = body
    if message.content_type is not None:
        if ContentTypes.text.value in message.content_type:
            m = body.decode()
        elif ContentTypes.json.value in message.content_type:  # pragma: no branch
            m = json.loads(body.decode())
    return m


def encode_message(msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
    if msg is None:
        return b"", None

    if isinstance(msg, bytes):
        return msg, None

    if isinstance(msg, str):
        return msg.encode(), ContentTypes.text.value

    return (
        dump_json(msg).encode(),
        ContentTypes.json.value,
    )
