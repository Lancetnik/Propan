from typing import Awaitable, Callable, Optional, Union

from typing_extensions import ParamSpec, Protocol, TypeAlias, TypeVar

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
T_HandlerReturn = TypeVar("T_HandlerReturn", bound=SendableMessage, covariant=True)

HandlerCallable: TypeAlias = Callable[
    ..., Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
]

HandlerWrapper: TypeAlias = Callable[
    [HandlerCallable[T_HandlerReturn]],
    HandlerCallable[T_HandlerReturn],
]


class AsyncWrappedHandlerCall(Protocol[MsgType, T_HandlerReturn]):
    async def __call__(
        self,
        __msg: PropanMessage[MsgType],
        reraise_exc: bool = False,
    ) -> Optional[T_HandlerReturn]:
        ...


class SyncWrappedHandlerCall(Protocol[MsgType, T_HandlerReturn]):
    def __call__(
        self,
        __msg: PropanMessage[MsgType],
        reraise_exc: bool = False,
    ) -> Optional[T_HandlerReturn]:
        ...


WrappedHandlerCall: TypeAlias = Union[
    AsyncWrappedHandlerCall[MsgType, T_HandlerReturn],
    SyncWrappedHandlerCall[MsgType, T_HandlerReturn],
]
