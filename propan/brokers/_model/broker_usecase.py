import json
import logging
import warnings
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack
from functools import wraps
from itertools import chain
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from fast_depends._compat import PYDANTIC_V2
from fast_depends.core import CallModel, build_call_model
from fast_depends.dependencies import Depends
from typing_extensions import Self, TypeAlias, TypeVar

from propan.brokers._model.routing import BrokerRouter
from propan.brokers._model.schemas import BaseHandler, PropanMessage
from propan.brokers._model.utils import (
    change_logger_handlers,
    get_watcher,
    set_message_context,
    suppress_decor,
    to_send,
)
from propan.brokers.constants import ContentType, ContentTypes
from propan.brokers.exceptions import SkipMessage
from propan.brokers.middlewares import BaseMiddleware
from propan.brokers.push_back_watcher import BaseWatcher
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import apply_types, context
from propan.utils.functions import get_function_positional_arguments, to_async

T = TypeVar("T", bound=DecodedMessage)

MsgType = TypeVar("MsgType")
ConnectionType = TypeVar("ConnectionType")

SyncParser: TypeAlias = Optional[
    Callable[
        [MsgType, Callable[[MsgType], PropanMessage[MsgType]]],
        PropanMessage[MsgType],
    ]
]
AsyncParser: TypeAlias = Optional[
    Callable[
        [MsgType, Callable[[MsgType], Awaitable[PropanMessage[MsgType]]]],
        Awaitable[PropanMessage[MsgType]],
    ]
]
SyncDecoder: TypeAlias = Optional[
    Callable[
        [
            PropanMessage[MsgType],
            Callable[[PropanMessage[MsgType]], DecodedMessage],
        ],
        DecodedMessage,
    ]
]
AsyncDecoder: TypeAlias = Optional[
    Callable[
        [
            PropanMessage[MsgType],
            Callable[[PropanMessage[MsgType]], Awaitable[DecodedMessage]],
        ],
        Awaitable[DecodedMessage],
    ]
]
CustomParser: TypeAlias = Union[AsyncParser[MsgType], SyncParser[MsgType]]
CustomDecoder: TypeAlias = Union[AsyncDecoder[MsgType], SyncDecoder[MsgType]]

T_HandlerReturn = TypeVar("T_HandlerReturn", bound=SendableMessage)

HandlerCallable: TypeAlias = Callable[
    ..., Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
]

HandlerWrapper: TypeAlias = Callable[
    [HandlerCallable[T_HandlerReturn]],
    HandlerCallable[T_HandlerReturn],
]


class BrokerUsecase(ABC, Generic[MsgType, ConnectionType]):
    logger: Optional[logging.Logger]
    log_level: int
    handlers: Sequence[BaseHandler]
    dependencies: Sequence[Depends]
    middlewares: Sequence[Type[BaseMiddleware[MsgType]]]
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
        middlewares: Sequence[Type[BaseMiddleware[MsgType]]] = (),
        # AsyncAPI
        protocol: str = "",
        protocol_version: Optional[str] = None,
        url_: Union[str, List[str]] = "",
        **kwargs: AnyDict,
    ) -> None:
        self.logger = logger
        self.log_level = log_level
        self._fmt = log_fmt

        self._connection = None
        self._is_apply_types = apply_types
        self.handlers = []
        self.dependencies = dependencies
        self.middlewares = middlewares

        self._connection_args = args
        self._connection_kwargs = kwargs

        self._global_parser = parse_message
        self._global_decoder = decode_message

        context.set_global("logger", logger)
        context.set_global("broker", self)

        self.protocol = protocol
        self.protocol_version = protocol_version
        self.url = url_
        self.started = False

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

    @staticmethod
    def _decode_message(message: PropanMessage[Any]) -> DecodedMessage:
        body = message.body
        m: DecodedMessage = body
        if message.content_type is not None:
            if ContentTypes.text.value in message.content_type:
                m = body.decode()
            elif ContentTypes.json.value in message.content_type:  # pragma: no branch
                m = json.loads(body.decode())
        return m

    @staticmethod
    def _encode_message(msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
        return to_send(msg)

    def include_router(self, router: BrokerRouter[MsgType]) -> None:
        for r in router.handlers:
            r.call = self.handle(*r.args, **r.kwargs)(r.call)

    def include_middleware(self, middleware: Type[BaseMiddleware[MsgType]]) -> None:
        self.middlewares = (*self.middlewares, middleware)

    def _wrap_handler(
        self,
        func: HandlerCallable[T_HandlerReturn],
        *,
        retry: Union[bool, int] = False,
        extra_dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[MsgType] = None,
        parse_message: CustomParser[MsgType] = None,
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        _is_sync: bool = False,
        **broker_log_context_kwargs: AnyDict,
    ) -> Tuple[
        Callable[
            [MsgType, bool],
            Union[
                Optional[T_HandlerReturn],
                Awaitable[Optional[T_HandlerReturn]],
            ],
        ],
        CallModel,
    ]:
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
            params=tuple(chain(dependant.flat_params, extra)),
            decoder=decode_message or self._global_decoder,
        )

        if self.logger is not None:
            f = self._log_execution(f, **broker_log_context_kwargs)

        f = self._wrap_middleware(f)

        f = self._process_message(
            func=f,
            watcher=get_watcher(self.logger, retry),
        )

        f = self._wrap_parse_message(
            func=f,
            parser=parse_message or self._global_parser,
        )

        f = set_message_context(f, _is_sync=_is_sync)

        return suppress_decor(f, _is_sync=_is_sync), dependant

    @property
    def fmt(self) -> str:  # pragma: no cover
        return self._fmt or ""

    def _get_log_context(
        self,
        message: Optional[PropanMessage[MsgType]],
        **kwargs: Dict[str, str],
    ) -> Dict[str, Any]:
        return {
            "message_id": message.message_id[:10] if message else "",
        }

    def _log(
        self,
        message: str,
        log_level: Optional[int] = None,
        extra: Optional[AnyDict] = None,
        **kwargs: AnyDict,
    ) -> None:
        if self.logger is not None:
            self.logger.log(
                level=(log_level or self.log_level),
                msg=message,
                extra=extra,
                **kwargs,
            )

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
    def handle(  # type: ignore[return]
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[MsgType] = None,
        parse_message: CustomParser[MsgType] = None,
        description: str = "",
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_kwargs: AnyDict,
    ) -> HandlerWrapper[T_HandlerReturn]:
        if self.started:
            warnings.warn(
                "You are trying to register `handler` with already running broker\n"  # noqa: E501
                "It has no effect until broker restarting.",  # noqa: E501
                category=RuntimeWarning,
                stacklevel=1,
            )

    @abstractmethod
    def _wrap_decode_message(
        self,
        func: HandlerCallable[T_HandlerReturn],
        decoder: CustomDecoder[MsgType],
        params: Sequence[Any] = (),
        _raw: bool = False,
    ) -> Callable[
        [PropanMessage[MsgType]], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
    ]:
        raise NotImplementedError()

    @abstractmethod
    def _wrap_parse_message(
        self,
        func: Callable[
            [PropanMessage[MsgType]], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
        ],
        parser: CustomParser[MsgType],
    ) -> Callable[[MsgType], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]]:
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

    @abstractmethod
    def _wrap_middleware(
        self,
        func: Callable[[MsgType], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]],
    ) -> Callable[[MsgType], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]]:
        raise NotImplementedError()


class BrokerAsyncUsecase(BrokerUsecase[MsgType, ConnectionType]):
    _global_parser: AsyncParser[MsgType]
    _global_decoder: AsyncDecoder[MsgType]

    @abstractmethod
    async def start(self) -> None:  # type: ignore[override]
        super().start()
        await self.connect()

    @abstractmethod
    async def _connect(self, **kwargs: AnyDict) -> ConnectionType:
        raise NotImplementedError()

    @abstractmethod
    async def close(  # type: ignore[override]
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        super().close()

    @abstractmethod
    def _process_message(  # type: ignore[override]
        self,
        func: Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        raise NotImplementedError()

    @abstractmethod
    async def _parse_message(self, message: MsgType) -> PropanMessage[MsgType]:
        raise NotImplementedError()

    @abstractmethod
    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: AnyDict,
    ) -> Optional[DecodedMessage]:
        raise NotImplementedError()

    @abstractmethod
    def handle(  # type: ignore[override,return]
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[MsgType] = None,
        parse_message: AsyncParser[MsgType] = None,
        description: str = "",
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[MsgType, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle(
            *broker_args,
            retry=retry,
            dependencies=dependencies,
            decode_message=decode_message,
            parse_message=parse_message,
            description=description,
            _raw=_raw,
            _get_dependant=_get_dependant,
            **broker_kwargs,
        )

    def __init__(
        self,
        *args: Any,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = "%(asctime)s %(levelname)s - %(message)s",
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[MsgType] = None,
        parse_message: AsyncParser[MsgType] = None,
        # AsyncAPI
        protocol: str = "",
        protocol_version: Optional[str] = None,
        url_: Union[str, List[str]] = "",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            *args,
            apply_types=apply_types,
            logger=logger,
            log_level=log_level,
            log_fmt=log_fmt,
            dependencies=dependencies,
            decode_message=decode_message,
            parse_message=parse_message,
            protocol=protocol,
            protocol_version=protocol_version,
            url_=url_,
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

    def _wrap_parse_message(  # type: ignore[override]
        self,
        func: Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]],
        parser: AsyncParser[MsgType],
    ) -> Callable[[MsgType], Awaitable[T_HandlerReturn]]:
        @wraps(func)
        async def parse_wrapper(message: MsgType) -> T_HandlerReturn:
            if parser is not None:
                m = await parser(message, self._parse_message)
            else:
                m = await self._parse_message(message)
            return await func(m)

        return parse_wrapper

    def _wrap_decode_message(  # type: ignore[override]
        self,
        func: Callable[..., Awaitable[T_HandlerReturn]],
        decoder: AsyncDecoder[MsgType],
        params: Sequence[Any] = (),
        _raw: bool = False,
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        is_unwrap = len(params) > 1

        @wraps(func)
        async def wrapper(message: PropanMessage[MsgType]) -> T_HandlerReturn:
            if decoder is not None:
                msg = await decoder(message, self._decode_message)
            else:
                msg = await self._decode_message(message)

            message.decoded_body = msg
            if _raw is True:
                return await func(message)

            elif is_unwrap is True:
                if isinstance(msg, Mapping):
                    return await func(**msg)
                else:
                    return await func(*msg)

            else:
                return await func(msg)

        return wrapper

    @classmethod
    # type: ignore[override]
    async def _decode_message(cls, message: PropanMessage[MsgType]) -> DecodedMessage:
        return super()._decode_message(message)

    def _wrap_handler(  # type: ignore[override]
        self,
        func: HandlerCallable[T_HandlerReturn],
        *,
        retry: Union[bool, int] = False,
        extra_dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[MsgType] = None,
        parse_message: AsyncParser[MsgType] = None,
        _raw: bool = False,
        _get_dependant: Callable[[Callable[..., Any]], CallModel] = build_call_model,
        **broker_log_context_kwargs: AnyDict,
    ) -> Tuple[
        Callable[
            [MsgType, bool],
            Awaitable[Optional[T_HandlerReturn]],
        ],
        CallModel,
    ]:
        return super()._wrap_handler(  # type: ignore[return-value]
            func,
            retry=retry,
            extra_dependencies=extra_dependencies,
            decode_message=decode_message,
            parse_message=parse_message,
            _raw=_raw,
            _get_dependant=_get_dependant,
            _is_sync=False,
            **broker_log_context_kwargs,
        )

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
                    self._log(repr(e), logging.ERROR, exc_info=e)
                    raise e
                else:
                    self._log("Processed", extra=log_context)
                    return r

        return log_wrapper

    def _wrap_middleware(
        self,
        func: Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]],
    ) -> Callable[[PropanMessage[MsgType]], Awaitable[T_HandlerReturn]]:
        @wraps(func)
        async def middleware_wrapper(msg: PropanMessage[MsgType]) -> T_HandlerReturn:
            async with AsyncExitStack() as stack:
                for m in self.middlewares:
                    await stack.enter_async_context(m(msg))
                return await func(msg)

        return middleware_wrapper


def extend_dependencies(extra: Sequence[CallModel]) -> Callable[[CallModel], CallModel]:
    def dependant_wrapper(dependant: CallModel) -> CallModel:
        if isinstance(dependant, CallModel):
            dependant.extra_dependencies.extend(extra)
        else:  # FastAPI dependencies
            dependant.dependencies.extend(extra)
        return dependant

    return dependant_wrapper
