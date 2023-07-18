from abc import abstractmethod
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, List, Optional, Tuple, Union

from propan.broker.message import PropanMessage
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
            Callable[F_Spec, F_Return],
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
        call: Callable[F_Spec, F_Return],
        wrapped_call: Callable[[MsgType, bool], F_Return],
        filter: Callable[[PropanMessage[MsgType]], bool] = lambda m: True,
    ) -> None:
        self.calls.append((call, wrapped_call, filter))

    @property
    def name(self) -> str:
        if not self.calls:
            return "Unknown"

        caller = self.calls[0][0]
        name = getattr(caller, "__name__", str(caller))
        return name

    @abstractmethod
    def consume(self, message: PropanMessage[MsgType]) -> None:
        for _, call, f in self.calls:
            if f(message):
                assert (
                    not message.processed
                ), "You can't proccess a message with multiple consumers"

                try:
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
class AsyncHandler(BaseHandler, Generic[MsgType]):
    calls: List[
        Tuple[
            Callable[F_Spec, Union[F_Return, Awaitable[F_Return]]],
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
        call: Callable[F_Spec, Union[F_Return, Awaitable[F_Return]]],
        wrapped_call: Callable[[MsgType, bool], Awaitable[F_Return]],
        filter: Callable[[PropanMessage[MsgType]], Awaitable[bool]] = lambda m: True,
    ) -> None:
        super().add_call(call, wrapped_call, filter)

    @abstractmethod
    async def consume(self, message: PropanMessage[MsgType]) -> None:
        result = None

        for _, call, f in self.calls:
            if await f(message):
                assert (
                    not message.processed
                ), "You can't proccess a message with multiple consumers"

                try:
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
