import inspect
from abc import abstractmethod
from contextlib import AsyncExitStack, ExitStack
from functools import partial
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    ContextManager,
    Generic,
    List,
    Optional,
    Tuple,
    Union,
    overload,
)

from fast_depends.core import CallModel

from propan._compat import IS_OPTIMIZED
from propan.asyncapi.base import AsyncAPIOperation
from propan.broker.message import PropanMessage
from propan.broker.schemas import HandlerCallWrapper
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
from propan.exceptions import StopConsume
from propan.types import F_Spec, SendableMessage, SendableReturn


async def async_default_filter(msg: PropanMessage[Any]) -> bool:
    return not msg.processed


class BaseHandler(AsyncAPIOperation, Generic[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[..., SendableMessage],  # original
            Callable[  # wrapped
                [PropanMessage[MsgType]],
                Optional[SendableMessage],
            ],
            Callable[[PropanMessage[MsgType]], bool],  # filter
            SyncParser[MsgType],  # parser
            SyncDecoder[MsgType],  # decoder
            List[  # middlewares
                Callable[[PropanMessage[MsgType]], ContextManager[None]]
            ],
            CallModel[..., SendableMessage],  # dependant
        ]
    ]

    global_middlewares: List[Callable[[MsgType], ContextManager[None]]]

    def __init__(
        self,
        *,
        description: Optional[str] = None,
    ):
        self.calls = []
        self.global_middlewares = []
        # AsyncAPI information
        self._description = description

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, SendableReturn],
        wrapped_call: Callable[[PropanMessage[MsgType]], Optional[SendableReturn]],
        parser: SyncParser[MsgType],
        decoder: SyncDecoder[MsgType],
        dependant: CallModel[F_Spec, SendableReturn],
        filter: Callable[
            [PropanMessage[MsgType]], bool
        ] = lambda m: not m.processed,  # pragma: no cover
        middlewares: Optional[
            List[Callable[[PropanMessage[MsgType]], ContextManager[None]]]
        ] = None,
    ) -> None:
        self.calls.append(
            (  # type: ignore
                handler,
                wrapped_call,
                filter,
                parser,
                decoder,
                middlewares or (),
                dependant,
            )
        )

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

    @overload
    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[SyncCustomDecoder[MsgType]],
        default_func: SyncDecoder[MsgType],
    ) -> SyncDecoder[MsgType]:
        ...

    @overload
    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[SyncCustomParser[MsgType]],
        default_func: SyncParser[MsgType],
    ) -> SyncParser[MsgType]:
        ...

    @overload
    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[AsyncCustomDecoder[MsgType]],
        default_func: AsyncDecoder[MsgType],
    ) -> AsyncDecoder[MsgType]:
        ...

    @overload
    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[AsyncCustomParser[MsgType]],
        default_func: AsyncParser[MsgType],
    ) -> AsyncParser[MsgType]:
        ...

    @staticmethod
    def _resolve_custom_func(
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


class AsyncHandler(BaseHandler[MsgType]):
    calls: List[  # type: ignore[assignment]
        Tuple[
            HandlerCallWrapper[..., SendableMessage],  # original
            Callable[  # wrapped
                [PropanMessage[MsgType]],
                Awaitable[Optional[SendableMessage]],
            ],
            Callable[[PropanMessage[MsgType]], Awaitable[bool]],  # filter
            AsyncParser[MsgType],  # parser
            AsyncDecoder[MsgType],  # decoder
            List[  # middlewares
                Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]
            ],
            CallModel[..., SendableMessage],  # dependant
        ]
    ]

    global_middlewares: List[  # type: ignore[assignment]
        Callable[[MsgType], AsyncContextManager[None]]
    ]

    def add_call(  # type: ignore[override]
        self,
        handler: HandlerCallWrapper[F_Spec, SendableReturn],
        wrapped_call: Callable[
            [PropanMessage[MsgType]],
            Awaitable[Optional[SendableReturn]],
        ],
        parser: AsyncParser[MsgType],
        decoder: AsyncDecoder[MsgType],
        dependant: CallModel[F_Spec, SendableReturn],
        filter: Callable[
            [PropanMessage[MsgType]], Awaitable[bool]
        ] = async_default_filter,
        middlewares: Optional[
            List[Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]]
        ] = None,
    ) -> None:
        self.calls.append(
            (  # type: ignore
                handler,
                wrapped_call,
                filter,
                parser,
                decoder,
                middlewares or (),
                dependant,
            )
        )

    async def consume(self, msg: MsgType) -> SendableMessage:  # type: ignore[override]
        result: SendableMessage = None

        async with AsyncExitStack() as stack:
            for m in self.global_middlewares:
                await stack.enter_async_context(m(msg))

            processed = False
            for handler, call, f, parser, decoder, middlewares, _ in self.calls:
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
    async def start(self) -> None:  # type: ignore[override]
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:  # type: ignore[override]
        raise NotImplementedError()
