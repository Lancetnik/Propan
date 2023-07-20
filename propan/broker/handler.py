from abc import abstractmethod
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, List, Optional, Tuple

from propan.broker.message import PropanMessage
from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import (
    AsyncDecoder,
    AsyncParser,
    CustomDecoder,
    CustomParser,
    MsgType,
)
from propan.exceptions import StopConsume
from propan.types import F_Return, F_Spec


@dataclass
class BaseHandler(Generic[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[F_Spec, F_Return],
            Callable[[MsgType, bool], F_Return],
            Callable[[PropanMessage[MsgType]], bool],
        ]
    ]

    custom_parser: Optional[CustomParser[MsgType]]
    custom_decoder: Optional[CustomDecoder[MsgType]]

    def __init__(
        self,
        custom_parser: Optional[CustomParser[MsgType]] = None,
        custom_decoder: Optional[CustomDecoder[MsgType]] = None,
    ):
        self.calls = []
        self.custom_parser = custom_parser
        self.custom_decoder = custom_decoder

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, F_Return],
        wrapped_call: Callable[[MsgType, bool], F_Return],
        filter: Callable[
            [PropanMessage[MsgType]], bool
        ] = lambda m: not m.processed,  # pragma: no cover
    ) -> None:
        self.calls.append((handler, wrapped_call, filter))

    @property
    def name(self) -> str:
        if not self.calls:
            return "undefined"

        caller = self.calls[0][0]
        name = getattr(caller, "__name__", str(caller))
        return name

    @abstractmethod
    def consume(self, message: PropanMessage[MsgType]) -> None:
        for handler, call, f in self.calls:
            if f(message):
                assert (
                    not message.processed
                ), "You can't proccess a message with multiple consumers"

                try:
                    handler.mock(message.decoded_body)
                    call(message)
                except StopConsume:
                    self.close()
                    return

                else:
                    message.processed = True

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError()


@dataclass
class AsyncHandler(BaseHandler[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[F_Spec, F_Return],
            Callable[[MsgType, bool], Awaitable[F_Return]],
            Callable[[PropanMessage[MsgType]], Awaitable[bool]],
        ]
    ]

    custom_parser: Optional[AsyncParser[MsgType]]
    custom_decoder: Optional[AsyncDecoder[MsgType]]

    def __init__(
        self,
        custom_parser: Optional[AsyncParser[MsgType]] = None,
        custom_decoder: Optional[AsyncDecoder[MsgType]] = None,
    ):
        super().__init__(
            custom_parser=custom_parser,
            custom_decoder=custom_decoder,
        )

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, F_Return],
        wrapped_call: Callable[
            [PropanMessage[MsgType], bool], Awaitable[Optional[F_Return]]
        ],
        filter: Callable[
            [PropanMessage[MsgType]], Awaitable[bool]
        ] = lambda m: not m.processed,
    ) -> None:
        super().add_call(handler, wrapped_call, filter)

    @abstractmethod
    async def consume(self, message: PropanMessage[MsgType]) -> None:
        result = None

        for handler, call, f in self.calls:
            if await f(message):
                assert (
                    not message.processed
                ), "You can't proccess a message with multiple consumers"

                try:
                    handler.mock(message.decoded_body)
                    result = await call(message)
                except StopConsume:
                    await self.close()
                    return
                else:
                    message.processed = True

        return result

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()
