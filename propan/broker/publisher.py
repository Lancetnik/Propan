from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, Optional
from unittest.mock import MagicMock

from propan.asyncapi.base import AsyncAPIOperation
from propan.broker.types import MsgType, P_HandlerParams, T_HandlerReturn
from propan.broker.wrapper import HandlerCallWrapper
from propan.types import AnyDict, DecodedMessage, SendableMessage


@dataclass
class BasePublisher(AsyncAPIOperation, Generic[MsgType]):
    title: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)

    calls: List[Callable[..., Any]] = field(
        init=False, default_factory=list, repr=False
    )
    mock: MagicMock = field(init=False, default_factory=MagicMock, repr=False)

    @property
    def channel_title(self) -> str:
        return self.title or self.calls[0].__name__.replace("_", " ").title().replace(
            " ", ""
        )

    def __call__(
        self,
        func: Callable[P_HandlerParams, T_HandlerReturn],
    ) -> HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn]:
        handler_call: HandlerCallWrapper[
            MsgType, P_HandlerParams, T_HandlerReturn
        ] = HandlerCallWrapper(func)
        handler_call._publishers.append(self)
        self.calls.append(handler_call._original_call)
        return handler_call

    @abstractmethod
    def publish(
        self,
        message: SendableMessage,
        correlation_id: Optional[str] = None,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        raise NotImplementedError()
