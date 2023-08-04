from typing import Awaitable, Callable, Optional, Union

from typing_extensions import ParamSpec, TypeAlias, TypeVar

from propan.broker.message import PropanMessage
from propan.types import DecodedMessage, SendableMessage

Decoded = TypeVar("Decoded", bound=DecodedMessage)
MsgType = TypeVar("MsgType")
ConnectionType = TypeVar("ConnectionType")

SyncParser: TypeAlias = Callable[
    [MsgType],
    PropanMessage[MsgType],
]
AsyncParser: TypeAlias = Callable[
    [MsgType],
    Awaitable[PropanMessage[MsgType]],
]
SyncCustomParser: TypeAlias = Callable[
    [MsgType, SyncParser[MsgType]],
    PropanMessage[MsgType],
]
AsyncCustomParser: TypeAlias = Callable[
    [MsgType, SyncParser[MsgType]],
    Awaitable[PropanMessage[MsgType]],
]
Parser: TypeAlias = Union[AsyncParser[MsgType], SyncParser[MsgType]]
CustomParser: TypeAlias = Union[AsyncCustomParser[MsgType], SyncCustomParser[MsgType]]

SyncDecoder: TypeAlias = Callable[
    [PropanMessage[MsgType]],
    DecodedMessage,
]
SyncCustomDecoder: TypeAlias = Callable[
    [PropanMessage[MsgType], SyncDecoder[MsgType]],
    DecodedMessage,
]
AsyncDecoder: TypeAlias = Callable[
    [
        PropanMessage[MsgType],
    ],
    Awaitable[DecodedMessage],
]
AsyncCustomDecoder: TypeAlias = Callable[
    [PropanMessage[MsgType], AsyncDecoder[MsgType]],
    Awaitable[DecodedMessage],
]
Decoder: TypeAlias = Union[AsyncDecoder[MsgType], SyncDecoder[MsgType]]
CustomDecoder: TypeAlias = Union[
    AsyncCustomDecoder[MsgType], SyncCustomDecoder[MsgType]
]

P_HandlerParams = ParamSpec("P_HandlerParams")
T_HandlerReturn = TypeVar("T_HandlerReturn", bound=SendableMessage)

HandlerCallable: TypeAlias = Callable[
    ..., Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
]

HandlerWrapper: TypeAlias = Callable[
    [HandlerCallable[T_HandlerReturn]],
    HandlerCallable[T_HandlerReturn],
]

SyncWrappedHandlerCall: TypeAlias = Callable[
    [PropanMessage[MsgType], bool], Optional[T_HandlerReturn]
]
AsyncWrappedHandlerCall: TypeAlias = Callable[
    [PropanMessage[MsgType], bool], Awaitable[Optional[T_HandlerReturn]]
]
WrappedHandlerCall: TypeAlias = Union[
    AsyncWrappedHandlerCall[MsgType, T_HandlerReturn],
    SyncWrappedHandlerCall[MsgType, T_HandlerReturn],
]
