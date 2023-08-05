import logging
from abc import abstractmethod
from functools import wraps
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Awaitable,
    Callable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from fast_depends.core import CallModel, build_call_model
from fast_depends.dependencies import Depends
from typing_extensions import Self

from propan.broker.core.abc import BrokerUsecase
from propan.broker.message import PropanMessage
from propan.broker.push_back_watcher import BaseWatcher
from propan.broker.types import (
    AsyncCustomDecoder,
    AsyncCustomParser,
    AsyncWrappedHandlerCall,
    ConnectionType,
    HandlerCallable,
    MsgType,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.exceptions import AckMessage, NackMessage, RejectMessage, SkipMessage
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context


class BrokerAsyncUsecase(BrokerUsecase[MsgType, ConnectionType]):
    middlewares: List[Callable[[MsgType], AsyncContextManager[None]]]
    _global_parser: AsyncCustomParser[MsgType]
    _global_decoder: AsyncCustomDecoder[MsgType]

    @abstractmethod
    async def start(self) -> None:  # type: ignore[override]
        super().start()
        await self.connect()

    @abstractmethod
    async def _connect(self, **kwargs: AnyDict) -> ConnectionType:
        raise NotImplementedError()

    @abstractmethod
    async def _close(  # type: ignore[override]
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        super()._close(exc_type, exc_val, exec_tb)

    async def close(  # type: ignore[override]
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        super().close(exc_type, exc_val, exec_tb)

        for h in self.handlers.values():
            await h.close()

        if self._connection is not None:
            await self._close(exc_type, exc_val, exec_tb)

    @abstractmethod
    def _process_message(  # type: ignore[override]
        self,
        func: Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]],
        call_wrapper: HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        raise NotImplementedError()

    @abstractmethod
    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        reply_to: str = "",
        rpc: bool = False,
        rpc_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        raise NotImplementedError()

    @abstractmethod
    def subscriber(  # type: ignore[override,return]
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decoder: AsyncCustomDecoder[MsgType] = None,
        parser: AsyncCustomParser[MsgType] = None,
        middlewares: Optional[
            List[
                Callable[
                    [PropanMessage[MsgType]],
                    AsyncContextManager[None],
                ]
            ]
        ] = None,
        filter: Callable[
            [PropanMessage[MsgType]], Awaitable[bool]
        ] = lambda m: not m.processed,
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        super().subscriber()

    def __init__(
        self,
        *args: Any,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = "%(asctime)s %(levelname)s - %(message)s",
        dependencies: Sequence[Depends] = (),
        decoder: AsyncCustomDecoder[MsgType] = None,
        parser: AsyncCustomParser[MsgType] = None,
        middlewares: Optional[
            List[
                Callable[
                    [MsgType],
                    AsyncContextManager[None],
                ]
            ]
        ] = None,
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            *args,
            apply_types=apply_types,
            logger=logger,
            log_level=log_level,
            log_fmt=log_fmt,
            dependencies=dependencies,
            decoder=decoder,
            parser=parser,
            middlewares=middlewares,
            **kwargs,
        )

    async def connect(  # type: ignore[override]
        self, *args: Any, **kwargs: AnyDict
    ) -> ConnectionType:
        if self._connection is None:
            _kwargs = self._resolve_connection_kwargs(*args, **kwargs)
            self._connection = await self._connect(**_kwargs)
        return self._connection

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exec_tb: Optional[TracebackType],
    ) -> None:
        await self.close(exc_type, exc_val, exec_tb)

    def _wrap_decode_message(  # type: ignore[override]
        self,
        func: Callable[..., Awaitable[T_HandlerReturn]],
        params: Sequence[Any] = (),
        _raw: bool = False,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        is_unwrap = len(params) > 1

        @wraps(func)
        async def decode_wrapper(message: PropanMessage[MsgType]) -> T_HandlerReturn:
            if _raw is True:
                return await func(message)

            msg = message.decoded_body

            if is_unwrap is True:
                if isinstance(msg, Mapping):
                    return await func(**msg)
                else:
                    return await func(*msg)

            else:
                return await func(msg)

        return decode_wrapper

    def _wrap_handler(  # type: ignore[override]
        self,
        func: HandlerCallable[T_HandlerReturn],
        *,
        retry: Union[bool, int] = False,
        extra_dependencies: Sequence[Depends] = (),
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_log_context_kwargs: AnyDict,
    ) -> Tuple[
        AsyncWrappedHandlerCall[MsgType, T_HandlerReturn],
        HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        CallModel[P_HandlerParams, T_HandlerReturn],
    ]:
        return super()._wrap_handler(  # type: ignore[return-value]
            func,
            retry=retry,
            extra_dependencies=extra_dependencies,
            _raw=_raw,
            _get_dependant=_get_dependant,
            _is_sync=False,
            **broker_log_context_kwargs,
        )

    async def _execute_handler(
        self,
        func: Callable[[PropanMessage], Awaitable[T_HandlerReturn]],
        message: PropanMessage[Any],
    ) -> T_HandlerReturn:
        try:
            return await func(message)
        except AckMessage as e:
            await message.ack()
            raise e
        except NackMessage as e:
            await message.nack()
            raise e
        except RejectMessage as e:
            await message.reject()
            raise e

    def _log_execution(  # type: ignore[override]
        self,
        func: Callable[
            [PropanMessage[MsgType]],
            Awaitable[T_HandlerReturn],
        ],
        **broker_args: AnyDict,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        @wraps(func)
        async def log_wrapper(message: PropanMessage[MsgType]) -> T_HandlerReturn:
            log_context = self._get_log_context(message=message, **broker_args)

            with context.scope("log_context", log_context):
                self._log("Received", extra=log_context)

                try:
                    r = await func(message)
                except SkipMessage as e:
                    self._log("Skipped", extra=log_context)
                    raise e
                except Exception as e:
                    self._log(f"{type(e).__name__}: {e}", logging.ERROR, exc_info=e)
                    raise e
                else:
                    self._log("Processed", extra=log_context)
                    return r

        return log_wrapper
