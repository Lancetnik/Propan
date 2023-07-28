import inspect
from abc import abstractmethod
from contextlib import AsyncExitStack, ExitStack
from functools import partial
from typing import (
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


class BaseHandler(Generic[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[F_Spec, F_Return],
            Callable[[MsgType, bool], F_Return],
            Callable[[PropanMessage[MsgType]], bool],
            CustomParser[MsgType],
            CustomDecoder[MsgType],
            List[Callable[[PropanMessage[MsgType]], ContextManager[None]]],
            CallModel[F_Spec, F_Return],
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
        self.call_middlewares = {}
        self.parsers = {}
        self.decoders = {}
        # AsyncAPI information
        self._description = description

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, F_Return],
        wrapped_call: Callable[[MsgType, bool], F_Return],
        parser: CustomParser[MsgType],
        decoder: CustomDecoder[MsgType],
        dependant: CallModel[F_Spec, F_Return],
        filter: Callable[
            [PropanMessage[MsgType]], bool
        ] = lambda m: not m.processed,  # pragma: no cover
        middlewares: Optional[
            List[Callable[[PropanMessage[MsgType]], ContextManager[None]]]
        ] = None,
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

    @property
    def name(self) -> str:
        if not self.calls:
            return "undefined"

        caller = self.calls[0][0]._original_call
        name = getattr(caller, "__name__", str(caller))
        return name

    @property
    def description(self) -> Optional[str]:
        if not self.calls:
            description = None

        else:
            caller = self.calls[0][0]._original_call
            description = getattr(caller, "__doc__", None)

        return self._description or description

    @abstractmethod
    def consume(self, msg: MsgType) -> None:
        result = None

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
                        not message.processed
                    ), "You can't proccess a message with multiple consumers"

                    try:
                        for m in middlewares:
                            stack.enter_context(m(message))

                        handler.mock(message.decoded_body)
                        result = call(message)
                    except StopConsume:
                        self.close()
                        return
                    else:
                        if IS_OPTIMIZED:
                            break
                        processed = True

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
        custom_func: Optional[CustomDecoder[MsgType]],
        default_func: CustomDecoder[MsgType],
    ) -> CustomDecoder[MsgType]:
        ...

    @overload
    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[CustomParser[MsgType]],
        default_func: CustomParser[MsgType],
    ) -> CustomParser[MsgType]:
        ...

    @staticmethod
    def _resolve_custom_func(
        custom_func: Optional[Union[CustomDecoder[MsgType], CustomParser[MsgType]]],
        default_func: Union[CustomDecoder[MsgType], CustomParser[MsgType]],
    ) -> Union[CustomDecoder[MsgType], CustomParser[MsgType]]:
        if custom_func is None:
            return default_func

        original_params = inspect.signature(custom_func).parameters
        assert (
            len(original_params) == 2
        ), "You should specify 2 incoming arguments: [<msg>, <original_function>]"
        name = tuple(original_params.items())[1][0]
        return partial(custom_func, **{name: default_func})


class AsyncHandler(BaseHandler[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[F_Spec, F_Return],
            Callable[[MsgType, bool], Awaitable[F_Return]],
            Callable[[PropanMessage[MsgType]], Awaitable[bool]],
            AsyncParser[MsgType],
            AsyncDecoder[MsgType],
            List[Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]],
        ]
    ]

    global_middlewares: List[Callable[[MsgType], AsyncContextManager[None]]]

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, F_Return],
        wrapped_call: Callable[
            [PropanMessage[MsgType], bool], Awaitable[Optional[F_Return]]
        ],
        parser: AsyncParser[MsgType],
        decoder: AsyncDecoder[MsgType],
        dependant: CallModel[F_Spec, F_Return],
        filter: Callable[
            [PropanMessage[MsgType]], Awaitable[bool]
        ] = lambda m: not m.processed,  # pragma: no cover
        middlewares: Optional[
            List[Callable[[PropanMessage[MsgType]], AsyncContextManager[None]]]
        ] = None,
    ) -> None:
        super().add_call(
            handler=handler,
            wrapped_call=wrapped_call,
            parser=parser,
            decoder=decoder,
            dependant=dependant,
            filter=filter,
            middlewares=middlewares,
        )

    async def consume(self, msg: MsgType) -> None:
        result = None

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
                        not message.processed
                    ), "You can't proccess a message with multiple consumers"

                    try:
                        for m in middlewares:
                            await stack.enter_async_context(m(message))

                        handler.mock(message.decoded_body)
                        result = await call(message)
                    except StopConsume:
                        await self.close()
                        return
                    else:
                        if IS_OPTIMIZED:
                            break
                        processed = True

        return result

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()
