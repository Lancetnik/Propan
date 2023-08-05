from typing import Callable, Generic, List, Optional, Union
from unittest.mock import MagicMock

from typing_extensions import Protocol, Self

from propan.broker.types import (
    MsgType,
    P_HandlerParams,
    T_HandlerReturn,
    WrappedHandlerCall,
)
from propan.types import AnyDict, DecodedMessage, SendableMessage


class AsyncPublisherProtocol(Protocol):
    def publish(
        self,
        message: SendableMessage,
        correlation_id: Optional[str] = None,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        ...


class HandlerCallWrapper(Generic[MsgType, P_HandlerParams, T_HandlerReturn]):
    mock: MagicMock

    _wrapped_call: Optional[WrappedHandlerCall[MsgType, T_HandlerReturn]]
    _original_call: Callable[P_HandlerParams, T_HandlerReturn]
    _publishers: List[AsyncPublisherProtocol]

    def __new__(
        cls,
        call: Union[
            "HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn]",
            Callable[P_HandlerParams, T_HandlerReturn],
        ],
    ) -> Self:
        if isinstance(call, cls):
            return call
        else:
            return super().__new__(cls)

    def __init__(
        self,
        call: Callable[P_HandlerParams, T_HandlerReturn],
    ):
        if not isinstance(call, HandlerCallWrapper):
            self._original_call = call
            self._wrapped_call = None
            self._publishers = []
            self.mock = MagicMock()
            self.__name__ = getattr(self._original_call, "__name__", "undefined")

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        self.mock(*args, **kwargs)
        return self._original_call(*args, **kwargs)
