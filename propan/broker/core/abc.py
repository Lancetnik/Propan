import logging
import warnings
from abc import ABC, abstractmethod
from itertools import chain
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from fast_depends._compat import PYDANTIC_V2
from fast_depends.core import CallModel, build_call_model
from fast_depends.dependencies import Depends

from propan.broker.core.mixins import LoggingMixin
from propan.broker.handler import BaseHandler
from propan.broker.message import PropanMessage
from propan.broker.push_back_watcher import BaseWatcher
from propan.broker.router import BrokerRouter
from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import (
    ConnectionType,
    CustomDecoder,
    CustomParser,
    HandlerCallable,
    MsgType,
    P_HandlerParams,
    T_HandlerReturn,
    WrappedHandlerCall,
)
from propan.broker.utils import (
    change_logger_handlers,
    get_watcher,
    set_message_context,
    suppress_decor,
)
from propan.log import access_logger
from propan.types import AnyDict
from propan.utils import apply_types, context
from propan.utils.functions import get_function_positional_arguments, to_async


class BrokerUsecase(
    ABC,
    Generic[MsgType, ConnectionType],
    LoggingMixin,
):
    logger: Optional[logging.Logger]
    log_level: int
    handlers: Dict[int, BaseHandler]
    dependencies: Sequence[Depends]
    started: bool
    _global_parser: CustomParser[MsgType]
    _global_decoder: CustomDecoder[MsgType]
    _connection: Optional[ConnectionType]
    _fmt: Optional[str]

    def __init__(
        self,
        *args: Any,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = "%(asctime)s %(levelname)s - %(message)s",
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[MsgType] = None,
        parse_message: CustomParser[MsgType] = None,
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(logger, log_level, log_fmt)

        self._connection = None
        self._is_apply_types = apply_types
        self.handlers = {}
        self.dependencies = dependencies

        self._connection_args = args
        self._connection_kwargs = kwargs

        self._global_parser = parse_message
        self._global_decoder = decode_message

        context.set_global("logger", logger)
        context.set_global("broker", self)

        self.started = False

    def include_router(self, router: BrokerRouter[MsgType]) -> None:
        for r in router.handlers:
            self.subscriber(*r.args, **r.kwargs)(r.call)

        for r in router.publishers:
            self.publisher(*r.args, **r.kwargs)(r.call)

    def _resolve_connection_kwargs(self, *args: Any, **kwargs: AnyDict) -> AnyDict:
        arguments = get_function_positional_arguments(self.__init__)  # type: ignore
        init_kwargs = {
            **self._connection_kwargs,
            **dict(zip(arguments, self._connection_args)),
        }

        connect_kwargs = {
            **kwargs,
            **dict(zip(arguments, args)),
        }
        return {**init_kwargs, **connect_kwargs}

    def _wrap_handler(
        self,
        func: HandlerCallable[T_HandlerReturn],
        *,
        retry: Union[bool, int] = False,
        extra_dependencies: Sequence[Depends] = (),
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        _is_sync: bool = False,
        **broker_log_context_kwargs: AnyDict,
    ) -> Tuple[
        WrappedHandlerCall[MsgType, T_HandlerReturn],
        HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        if isinstance(func, HandlerCallWrapper):
            handler_call, func = func, func._original_call

        else:
            handler_call = HandlerCallWrapper(func)

        dependant = _get_dependant(func)

        extra = [
            _get_dependant(d.dependency)
            for d in chain(extra_dependencies, self.dependencies)
        ]

        extend_dependencies(extra)(dependant)

        if getattr(dependant, "flat_params", None) is None:  # handle FastAPI Dependant
            params = dependant.query_params + dependant.body_params

            for d in dependant.dependencies:
                params.extend(d.query_params + d.body_params)

            params_unique = {}
            params_names = set()
            for p in params:
                if p.name not in params_names:
                    params_names.add(p.name)
                    if PYDANTIC_V2:
                        params_unique[p.name] = p.field_info
                    else:
                        # TODO: remove it with stable PydanticV2
                        params_unique[p.name] = p

            dependant.flat_params = params_unique

        # f: Any
        if _is_sync:
            f = func
        else:
            f = to_async(func)

        if self._is_apply_types is True:
            f = apply_types(
                func=f,
                wrap_model=extend_dependencies(extra),
            )

        f = self._wrap_decode_message(
            func=f,
            _raw=_raw,
            params=tuple(chain(dependant.flat_params.items(), extra)),
        )

        f = self._process_message(
            func=f,
            call_wrapper=handler_call,
            watcher=get_watcher(self.logger, retry),
        )

        if self.logger is not None:
            f = self._log_execution(f, **broker_log_context_kwargs)

        f = set_message_context(f)

        return suppress_decor(f), handler_call

    # Final Broker Impl
    @abstractmethod
    def start(self) -> None:
        self.started = True

        if self.logger is not None:
            change_logger_handlers(self.logger, self.fmt)

    @abstractmethod
    def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        self.started = False

    @abstractmethod
    def _process_message(
        self,
        func: Callable[
            [PropanMessage[MsgType]], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
        ],
        call_wrapper: HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        watcher: Optional[BaseWatcher],
    ) -> Callable[
        [PropanMessage[MsgType]], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
    ]:
        raise NotImplementedError()

    # Async and Sync Inherits Impl
    @abstractmethod
    def connect(self, *args: Any, **kwargs: AnyDict) -> ConnectionType:
        raise NotImplementedError()

    @abstractmethod
    def _execute_handler(
        self,
        func: Callable[[PropanMessage], T_HandlerReturn],
        message: PropanMessage[Any],
    ) -> T_HandlerReturn:
        raise NotImplementedError()

    @abstractmethod
    def subscriber(  # type: ignore[return]
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: Optional[CustomDecoder[MsgType]] = None,
        parse_message: Optional[CustomParser[MsgType]] = None,
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        if self.started:
            warnings.warn(
                "You are trying to register `handler` with already running broker\n"  # noqa: E501
                "It has no effect until broker restarting.",  # noqa: E501
                category=RuntimeWarning,
                stacklevel=1,
            )

    @abstractmethod
    def publisher(
        self,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
    ]:
        raise NotImplementedError()

    @abstractmethod
    def _wrap_decode_message(
        self,
        func: HandlerCallable[T_HandlerReturn],
        params: Sequence[Any] = (),
        _raw: bool = False,
    ) -> Callable[
        [PropanMessage[MsgType]], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
    ]:
        raise NotImplementedError()

    @abstractmethod
    def _log_execution(
        self,
        func: Callable[
            [PropanMessage[MsgType]],
            Union[
                T_HandlerReturn,
                Awaitable[T_HandlerReturn],
            ],
        ],
        **broker_args: AnyDict,
    ) -> Callable[
        [PropanMessage[MsgType]],
        Union[
            T_HandlerReturn,
            Awaitable[T_HandlerReturn],
        ],
    ]:
        raise NotImplementedError()


def extend_dependencies(extra: Sequence[CallModel]) -> Callable[[CallModel], CallModel]:
    def dependant_wrapper(dependant: CallModel) -> CallModel:
        if isinstance(dependant, CallModel):
            dependant.extra_dependencies.extend(extra)
        else:  # FastAPI dependencies
            dependant.dependencies.extend(extra)
        return dependant

    return dependant_wrapper
