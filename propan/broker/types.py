from typing import Awaitable, Callable, Optional, Union

from typing_extensions import ParamSpec, TypeAlias, TypeVar

from propan.broker.message import PropanMessage
from propan.types import DecodedMessage, SendableMessage

Decoded = TypeVar("Decoded", bound=DecodedMessage)
MsgType = TypeVar("MsgType")
ConnectionType = TypeVar("ConnectionType")

SyncParser: TypeAlias = Optional[
    Callable[
        [MsgType, Callable[[MsgType], PropanMessage[MsgType]]],
        PropanMessage[MsgType],
    ]
]
AsyncParser: TypeAlias = Optional[
    Callable[
        [MsgType, Callable[[MsgType], Awaitable[PropanMessage[MsgType]]]],
        Awaitable[PropanMessage[MsgType]],
    ]
]
SyncDecoder: TypeAlias = Optional[
    Callable[
        [
            PropanMessage[MsgType],
            Callable[[PropanMessage[MsgType]], DecodedMessage],
        ],
        DecodedMessage,
    ]
]
AsyncDecoder: TypeAlias = Optional[
    Callable[
        [
            PropanMessage[MsgType],
            Callable[[PropanMessage[MsgType]], Awaitable[DecodedMessage]],
        ],
        Awaitable[DecodedMessage],
    ]
]
CustomParser: TypeAlias = Union[AsyncParser[MsgType], SyncParser[MsgType]]
CustomDecoder: TypeAlias = Union[AsyncDecoder[MsgType], SyncDecoder[MsgType]]

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
