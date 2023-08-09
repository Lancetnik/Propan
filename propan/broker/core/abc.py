import logging
import warnings
from abc import ABC, abstractmethod
from itertools import chain
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    ContextManager,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from fast_depends._compat import PYDANTIC_V2
from fast_depends.core import CallModel, build_call_model
from fast_depends.dependencies import Depends
from fast_depends.use import _InjectWrapper

from propan import asyncapi
from propan.broker.core.mixins import LoggingMixin
from propan.broker.handler import BaseHandler
from propan.broker.message import PropanMessage
from propan.broker.middlewares import CriticalLogMiddleware
from propan.broker.publisher import BasePublisher
from propan.broker.push_back_watcher import BaseWatcher
from propan.broker.router import BrokerRouter
from propan.broker.types import (
    ConnectionType,
    CustomDecoder,
    CustomParser,
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
from propan.broker.wrapper import HandlerCallWrapper
from propan.log import access_logger
from propan.types import AnyDict, F_Return, F_Spec
from propan.utils import apply_types, context
from propan.utils.functions import get_function_positional_arguments, to_async


class BrokerUsecase(
    ABC,
    Generic[MsgType, ConnectionType],
    LoggingMixin,
):
    logger: Optional[logging.Logger]
    log_level: int
    handlers: Dict[Any, BaseHandler[MsgType]]
    _publishers: Dict[Any, BasePublisher[MsgType]]

    dependencies: Sequence[Depends]
    started: bool
    middlewares: Sequence[Callable[[MsgType], ContextManager[None]]]
    _global_parser: Optional[CustomParser[MsgType]]
    _global_decoder: Optional[CustomDecoder[MsgType]]
    _connection: Optional[ConnectionType]
    _fmt: Optional[str]

    def __init__(
        self,
        url: Union[str, List[str]],
        *args: Any,
        # AsyncAPI kwargs
        protocol: str,
        protocol_version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Sequence[asyncapi.Tag]] = None,
        # broker kwargs
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = "%(asctime)s %(levelname)s - %(message)s",
        dependencies: Sequence[Depends] = (),
        middlewares: Optional[
            Iterable[Callable[[MsgType], ContextManager[None]]]
        ] = None,
        decoder: Optional[CustomDecoder[MsgType]] = None,
        parser: Optional[CustomParser[MsgType]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            logger=logger,
            log_level=log_level,
            log_fmt=log_fmt,
        )

        self._connection = None
        self._is_apply_types = apply_types
        self.handlers = {}
        self._publishers = {}
        self.middlewares = [CriticalLogMiddleware(logger), *(middlewares or ())]  # type: ignore
        self.dependencies = dependencies

        self._connection_args = args
        self._connection_kwargs = kwargs

        self._global_parser = parser
        self._global_decoder = decoder

        context.set_global("logger", logger)
        context.set_global("broker", self)

        self.started = False

        # AsyncAPI information
        self.url = url
        self.protocol = protocol
        self.protocol_version = protocol_version
        self.description = description
        self.tags = tags

    def include_router(self, router: BrokerRouter[MsgType]) -> None:
        for r in router._handlers:
            self.subscriber(*r.args, **r.kwargs)(r.call)

        self._publishers.update(router._publishers)

    def _resolve_connection_kwargs(self, *args: Any, **kwargs: Any) -> AnyDict:
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
        func: Union[
            HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
            Callable[P_HandlerParams, T_HandlerReturn],
        ],
        *,
        retry: Union[bool, int] = False,
        extra_dependencies: Sequence[Depends] = (),
        _raw: bool = False,
        _get_dependant: Optional[Any] = None,
        **broker_log_context_kwargs: Any,
    ) -> Tuple[
        WrappedHandlerCall[MsgType, T_HandlerReturn],
        HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
        Union[
            CallModel[P_HandlerParams, T_HandlerReturn],
            CallModel[P_HandlerParams, Awaitable[T_HandlerReturn]],
        ],
    ]:
        build_dep = cast(
            Callable[[Callable[F_Spec, F_Return]], CallModel[F_Spec, F_Return]],
            _get_dependant or build_call_model,
        )

        if isinstance(func, HandlerCallWrapper):
            handler_call, func = func, func._original_call
            if handler_call._wrapped_call is not None:
                return handler_call._wrapped_call, handler_call, build_dep(func)
        else:
            handler_call = HandlerCallWrapper(func)

        f = to_async(func)

        dependant = build_dep(f)

        extra = [
            build_dep(d.dependency)
            for d in chain(extra_dependencies, self.dependencies)
        ]

        extend_dependencies(extra, dependant)

        if getattr(dependant, "flat_params", None) is None:  # handle FastAPI Dependant
            params = dependant.query_params + dependant.body_params  # type: ignore[attr-defined]

            for d in dependant.dependencies:
                params.extend(d.query_params + d.body_params)  # type: ignore[attr-defined]

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

            # TODO: build model for AsyncAPI scheme
            # dependant.model = build_model(...)
            dependant.flat_params = params_unique  # type: ignore[misc]

        if self._is_apply_types is True:
            apply_wrapper = cast(
                _InjectWrapper[P_HandlerParams, Awaitable[T_HandlerReturn]],
                apply_types(None),
            )
            f = apply_wrapper(f, dependant)

        decode_f = self._wrap_decode_message(
            func=f,
            _raw=_raw,
            params=tuple(chain(dependant.flat_params.values(), extra)),
        )

        process_f = self._process_message(
            func=decode_f,
            call_wrapper=handler_call,
            watcher=get_watcher(self.logger, retry),
        )

        if self.logger is not None:
            process_f = self._log_execution(process_f, **broker_log_context_kwargs)

        process_f = set_message_context(process_f)
        suppress_f = suppress_decor(process_f)

        handler_call._wrapped_call = suppress_f
        return suppress_f, handler_call, dependant

    def _abc_start(self) -> None:
        self.started = True

        for h in self.handlers.values():
            h.global_middlewares = (*self.middlewares, *h.global_middlewares)

        if self.logger is not None:
            change_logger_handlers(self.logger, self.fmt)

    def _abc_close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        self.started = False

    def _abc__close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        self._connection = None

    @abstractmethod
    def _process_message(
        self,
        func: Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]],
        call_wrapper: HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
        watcher: BaseWatcher,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        raise NotImplementedError()

    @abstractmethod
    def subscriber(  # type: ignore[return]
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decoder: Optional[CustomDecoder[MsgType]] = None,
        parser: Optional[CustomParser[MsgType]] = None,
        middlewares: Optional[
            Iterable[
                Callable[
                    [PropanMessage[MsgType]],
                    ContextManager[None],
                ]
            ]
        ] = None,
        filter: Callable[
            [PropanMessage[MsgType]], Union[bool, Awaitable[bool]]
        ] = lambda m: not m.processed,
        _raw: bool = False,
        _get_dependant: Optional[Any] = None,
        **broker_kwargs: Any,
    ) -> Callable[
        [
            Union[
                Callable[P_HandlerParams, T_HandlerReturn],
                HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
            ]
        ],
        HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn],
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
        key: Any,
        publisher: BasePublisher[MsgType],
    ) -> BasePublisher[MsgType]:
        self._publishers[key] = publisher
        return publisher

    @abstractmethod
    def _wrap_decode_message(
        self,
        func: Callable[..., Awaitable[T_HandlerReturn]],
        params: Sequence[Any] = (),
        _raw: bool = False,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        raise NotImplementedError()

    @abstractmethod
    def _log_execution(
        self,
        func: Callable[
            [PropanMessage[MsgType]],
            Awaitable[T_HandlerReturn],
        ],
        **broker_args: Any,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn],]:
        raise NotImplementedError()


def extend_dependencies(
    extra: Sequence[CallModel[..., Any]], dependant: CallModel[..., Any]
) -> CallModel[..., Any]:
    if isinstance(dependant, CallModel):
        dependant.extra_dependencies = (*dependant.extra_dependencies, *extra)
    else:  # FastAPI dependencies
        dependant.dependencies.extend(extra)
    return dependant
