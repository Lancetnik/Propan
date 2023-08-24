from abc import abstractmethod
from contextlib import AsyncExitStack
from typing import (
    Any,
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
    cast,
)

from fast_depends.core import CallModel

from propan._compat import IS_OPTIMIZED, override
from propan.asyncapi.base import AsyncAPIOperation
from propan.asyncapi.utils import to_camelcase
from propan.broker.message import PropanMessage
from propan.broker.types import (
    AsyncDecoder,
    AsyncParser,
    MsgType,
    P_HandlerParams,
    SyncDecoder,
    SyncParser,
    T_HandlerReturn,
    WrappedReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.exceptions import StopConsume
from propan.types import SendableMessage


class BaseHandler(AsyncAPIOperation, Generic[MsgType]):
    calls: Union[
        List[
            Tuple[
                HandlerCallWrapper[MsgType, Any, SendableMessage],  # handler
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
                HandlerCallWrapper[MsgType, Any, SendableMessage],  # handler
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
    is_test: bool

    def __init__(
        self,
        *,
        description: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.calls = []  # type: ignore[assignment]
        self.global_middlewares = []
        # AsyncAPI information
        self._description = description
        self._title = title
        self.is_test = False

    def set_test(self) -> None:
        self.is_test = True

    @override
    @property
    def name(self) -> Union[str, bool]:  # type: ignore[override]
        if self._title:
            return self._title

        if not self.calls:  # pragma: no cover
            return False

        else:
            return True

    @property
    def call_name(self) -> str:
        caller = self.calls[0][0]._original_call
        name = getattr(caller, "__name__", str(caller))
        return to_camelcase(name)

    @property
    def description(self) -> Optional[str]:
        if not self.calls:  # pragma: no cover
            description = None

        else:
            caller = self.calls[0][0]._original_call
            description = getattr(caller, "__doc__", None)

        return self._description or description

    @abstractmethod
    def consume(self, msg: MsgType) -> SendableMessage:
        raise NotImplementedError()


class AsyncHandler(BaseHandler[MsgType]):
    calls: List[
        Tuple[
            HandlerCallWrapper[MsgType, Any, SendableMessage],  # handler
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
                filter,
                parser,
                decoder,
                middlewares or (),
                dependant,
            )
        )

    @override
    async def consume(self, msg: MsgType) -> SendableMessage:  # type: ignore[override]
        result: Optional[WrappedReturn[SendableMessage]] = None
        result_msg: SendableMessage = None

        async with AsyncExitStack() as stack:
            for m in self.global_middlewares:
                await stack.enter_async_context(m(msg))

            processed = False
            for handler, f, parser, decoder, middlewares, _ in self.calls:
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

                        result = await cast(
                            Awaitable[Optional[WrappedReturn[SendableMessage]]],
                            handler.call_wrapped(message, reraise_exc=self.is_test),
                        )

                        if result is not None:
                            result_msg, pub_response = result

                            for publisher in (pub_response, *handler._publishers):
                                if publisher is not None:
                                    await publisher.publish(
                                        message=result_msg,
                                        correlation_id=message.correlation_id,
                                    )

                    except StopConsume:
                        await self.close()
                        return None

                    else:
                        message.processed = processed = True
                        if IS_OPTIMIZED:  # pragma: no cover
                            break

        return result_msg

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()
