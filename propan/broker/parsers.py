import inspect
import json
from functools import partial
from typing import Any, Optional, Tuple, Union, overload

from propan._compat import dump_json
from propan.broker.message import PropanMessage
from propan.broker.types import (
    AsyncCustomDecoder,
    AsyncCustomParser,
    AsyncDecoder,
    AsyncParser,
    CustomDecoder,
    CustomParser,
    Decoder,
    MsgType,
    Parser,
    SyncCustomDecoder,
    SyncCustomParser,
    SyncDecoder,
    SyncParser,
)
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


@overload
def resolve_custom_func(
    custom_func: Optional[SyncCustomDecoder[MsgType]],
    default_func: SyncDecoder[MsgType],
) -> SyncDecoder[MsgType]:
    ...


@overload
def resolve_custom_func(
    custom_func: Optional[SyncCustomParser[MsgType]],
    default_func: SyncParser[MsgType],
) -> SyncParser[MsgType]:
    ...


@overload
def resolve_custom_func(
    custom_func: Optional[AsyncCustomDecoder[MsgType]],
    default_func: AsyncDecoder[MsgType],
) -> AsyncDecoder[MsgType]:
    ...


@overload
def resolve_custom_func(
    custom_func: Optional[AsyncCustomParser[MsgType]],
    default_func: AsyncParser[MsgType],
) -> AsyncParser[MsgType]:
    ...


def resolve_custom_func(
    custom_func: Optional[Union[CustomDecoder[MsgType], CustomParser[MsgType]]],
    default_func: Union[Decoder[MsgType], Parser[MsgType]],
) -> Union[Decoder[MsgType], Parser[MsgType]]:
    if custom_func is None:
        return default_func

    original_params = inspect.signature(custom_func).parameters
    assert (
        len(original_params) == 2
    ), "You should specify 2 incoming arguments: [<msg>, <original_function>]"
    name = tuple(original_params.items())[1][0]
    return partial(custom_func, **{name: default_func})  # type: ignore
