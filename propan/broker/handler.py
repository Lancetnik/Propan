from abc import abstractmethod
from contextlib import AsyncExitStack, ExitStack
from typing import (
    AsyncContextManager,
    Awaitable,
    Callable,
    ContextManager,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from fast_depends.core import CallModel
from typing_extensions import override

from propan._compat import IS_OPTIMIZED
from propan.asyncapi.base import AsyncAPIOperation
from propan.broker.message import PropanMessage
from propan.broker.types import (
    AsyncDecoder,
    AsyncParser,
    AsyncWrappedHandlerCall,
    MsgType,
    P_HandlerParams,
    SyncDecoder,
    SyncParser,
    SyncWrappedHandlerCall,
    T_HandlerReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.exceptions import StopConsume
from propan.types import SendableMessage


class BaseHandler(AsyncAPIOperation, Generic[MsgType]):
    calls: Union[
        List[
            Tuple[
                HandlerCallWrapper[MsgType, ..., SendableMessage],  # original
                SyncWrappedHandlerCall[MsgType, SendableMessage],  # wrapped
                Callable[[PropanMessage[MsgType]], bool],  # filter
                SyncParser[MsgType],  # parser
                SyncDecoder[MsgType],  # decoder
                Sequence[  # middlewares
                    Callable[[PropanMessage[MsgType]], ContextManager[None]]
                ],
                CallModel[..., SendableMessage],  # dependant
            ]
        ],
        List[
            Tuple[
                HandlerCallWrapper[MsgType, ..., SendableMessage],  # original
                AsyncWrappedHandlerCall[MsgType, SendableMessage],  # wrapped[]],
                Callable[[PropanMessage[MsgType]], Awaitable[bool]],  # filter
                AsyncParser[MsgType],  # parser
                AsyncDecoder[MsgType],  # decoder
                Sequence[  # middlewares
                    Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]
                ],
                CallModel[..., SendableMessage],  # dependant
            ]
        ],
    ]

    global_middlewares: Union[
        Sequence[Callable[[MsgType], ContextManager[None]]],
        Sequence[Callable[[MsgType], AsyncContextManager[None]]],
    ]

    def __init__(
        self,
        *,
        description: Optional[str] = None,
    ):
        self.calls = []  # type: ignore[assignment]
        self.global_middlewares = []
        # AsyncAPI information
        self._description = description

    @property
    def name(self) -> str:
        if not self.calls:
            return "undefined"

        caller = self.calls[0][0]._original_call
        name = getattr(caller, "__name__", str(caller))
        return name.replace("_", " ").title().replace(" ", "")

    @property
    def description(self) -> Optional[str]:
        if not self.calls:
            description = None

        else:
            caller = self.calls[0][0]._original_call
            description = getattr(caller, "__doc__", None)

        return self._description or description

    @abstractmethod
    def consume(self, msg: MsgType) -> SendableMessage:
        raise NotImplementedError()


class SyncHandler(BaseHandler[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[MsgType, ..., SendableMessage],  # original
            SyncWrappedHandlerCall[MsgType, SendableMessage],  # wrapped
            Callable[[PropanMessage[MsgType]], bool],  # filter
            SyncParser[MsgType],  # parser
            SyncDecoder[MsgType],  # decoder
            Sequence[  # middlewares
                Callable[[PropanMessage[MsgType]], ContextManager[None]]
            ],
            CallModel[..., SendableMessage],  # dependant
        ]
    ]

    global_middlewares: Sequence[Callable[[MsgType], ContextManager[None]]]

    def add_call(
        self,
        *,
        handler: HandlerCallWrapper[MsgType, ..., SendableMessage],
        wrapped_call: SyncWrappedHandlerCall[MsgType, SendableMessage],
        filter: Callable[[PropanMessage[MsgType]], bool],
        parser: SyncParser[MsgType],
        decoder: SyncDecoder[MsgType],
        middlewares: Optional[
            Sequence[Callable[[PropanMessage[MsgType]], ContextManager[None]]]
        ],
        dependant: CallModel[..., SendableMessage],
    ) -> None:
        self.calls.append(
            (
                handler,
                wrapped_call,
                filter,
                parser,
                decoder,
                middlewares or (),
                dependant,
            )
        )

    def consume(self, msg: MsgType) -> SendableMessage:
        result: SendableMessage = None

        with ExitStack() as stack:
            for m in self.global_middlewares:
                stack.enter_context(m(msg))

            processed = False
            for handler, call, f, parser, decoder, middlewares, _ in self.calls:
                message = parser(msg)
                message.decoded_body = decoder(message)
                message.processed = processed

                if f(message):
                    assert (
                        not processed
                    ), "You can't proccess a message with multiple consumers"

                    try:
                        for inner_m in middlewares:
                            stack.enter_context(inner_m(message))

                        handler.mock(message.decoded_body)
                        result = call(message)

                    except StopConsume:
                        self.close()
                        return None

                    else:
                        message.processed = processed = True
                        if IS_OPTIMIZED:
                            break

        return result

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError()


class AsyncHandler(BaseHandler[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[MsgType, ..., SendableMessage],  # original
            AsyncWrappedHandlerCall[MsgType, SendableMessage],  # wrapped[]],
            Callable[[PropanMessage[MsgType]], Awaitable[bool]],  # filter
            AsyncParser[MsgType],  # parser
            AsyncDecoder[MsgType],  # decoder
            Sequence[  # middlewares
                Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]
            ],
            CallModel[..., SendableMessage],  # dependant
        ]
    ]

    global_middlewares: Sequence[Callable[[MsgType], AsyncContextManager[None]]]

    def add_call(
        self,
        *,
        handler: HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
        wrapped_call: AsyncWrappedHandlerCall[MsgType, T_HandlerReturn],
        parser: AsyncParser[MsgType],
        decoder: AsyncDecoder[MsgType],
        dependant: CallModel[P_HandlerParams, T_HandlerReturn],
        filter: Callable[[PropanMessage[MsgType]], Awaitable[bool]],
        middlewares: Optional[
            Sequence[Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]]
        ],
    ) -> None:
        self.calls.append(
            (  # type: ignore[arg-type]
                handler,
                wrapped_call,
                filter,
                parser,
                decoder,
                middlewares or (),
                dependant,
            )
        )

    @override
    async def consume(self, msg: MsgType) -> SendableMessage:  # type: ignore[override]
        result: SendableMessage = None

        async with AsyncExitStack() as stack:
            for m in self.global_middlewares:
                await stack.enter_async_context(m(msg))

            processed = False
            for handler, call, f, parser, decoder, middlewares, _ in self.calls:
                # TODO: add parser & decoder cashes
                message = await parser(msg)
                message.decoded_body = await decoder(message)
                message.processed = processed

                if await f(message):
                    assert (
                        not processed
                    ), "You can't proccess a message with multiple consumers"

                    try:
                        for inner_m in middlewares:
                            await stack.enter_async_context(inner_m(message))

                        handler.mock(message.decoded_body)
                        result = await call(message)

                    except StopConsume:
                        await self.close()
                        return None

                    else:
                        message.processed = processed = True
                        if IS_OPTIMIZED:
                            break

        return result

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()
