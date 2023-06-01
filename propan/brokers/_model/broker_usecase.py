import json
import logging
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from typing_extensions import Self

from propan.brokers._model.schemas import (
    ContentType,
    ContentTypes,
    PropanMessage,
    SendableModel,
)
from propan.brokers._model.utils import (
    change_logger_handlers,
    get_watcher,
    set_message_context,
    suppress_decor,
)
from propan.brokers.exceptions import SkipMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.log import access_logger
from propan.types import (
    AnyCallable,
    AnyDict,
    DecodedMessage,
    DecoratedAsync,
    HandlerWrapper,
    SendableMessage,
    Wrapper,
)
from propan.utils import apply_types, context
from propan.utils.functions import to_async

T = TypeVar("T")


class BrokerUsecase(ABC):
    logger: Optional[logging.Logger]
    log_level: int
    handlers: List[Any]
    _connection: Any
    _fmt: Optional[str]

    def __init__(
        self,
        *args: Any,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = "%(asctime)s %(levelname)s - %(message)s",
        **kwargs: Any,
    ) -> None:
        self.logger = logger
        self.log_level = log_level
        self._fmt = log_fmt

        self._connection = None
        self._is_apply_types = apply_types
        self.handlers = []

        self._connection_args = args
        self._connection_kwargs = kwargs

        context.set_global("logger", logger)
        context.set_global("broker", self)

    async def connect(self, *args: Any, **kwargs: Any) -> Any:
        if self._connection is None:
            _args = args or self._connection_args
            _kwargs = kwargs or self._connection_kwargs
            self._connection = await self._connect(*_args, **_kwargs)
        return self._connection

    @abstractmethod
    async def _connect(self, *args: Any, **kwargs: Any) -> Any:
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
        **kwargs: Any,
    ) -> Optional[DecodedMessage]:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def _parse_message(self, message: Any) -> PropanMessage:
        raise NotImplementedError()

    @abstractmethod
    def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]:
        raise NotImplementedError()

    def _get_log_context(
        self,
        message: Optional[PropanMessage],
        **kwargs: Dict[str, str],
    ) -> Dict[str, Any]:
        return {
            "message_id": message.message_id[:10] if message else "",
        }

    @abstractmethod
    def handle(
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        _raw: bool = False,
        **broker_kwargs: Any,
    ) -> HandlerWrapper:
        raise NotImplementedError()

    @staticmethod
    async def _decode_message(message: PropanMessage) -> DecodedMessage:
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
        return SendableModel.to_send(msg)

    @property
    def fmt(self) -> str:  # pragma: no cover
        return self._fmt or ""

    async def start(self) -> None:
        if self.logger is not None:
            change_logger_handlers(self.logger, self.fmt)

        await self.connect()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()

    def _wrap_handler(
        self,
        func: AnyCallable,
        retry: Union[bool, int] = False,
        _raw: bool = False,
        **broker_args: Any,
    ) -> DecoratedAsync:
        f = to_async(func)

        if self._is_apply_types is True:
            f = apply_types(f)

        f = self._wrap_decode_message(f, _raw=_raw)

        if self.logger is not None:
            f = self._log_execution(**broker_args)(f)

        f = self._process_message(f, get_watcher(self.logger, retry))

        f = self._wrap_parse_message(f)

        f = set_message_context(f)

        f = suppress_decor(f)

        return f

    def _wrap_decode_message(
        self,
        func: Callable[..., Awaitable[T]],
        _raw: bool = False,
    ) -> Callable[[PropanMessage], Awaitable[T]]:
        decode: Callable[
            [PropanMessage], Awaitable[Union[PropanMessage, DecodedMessage]]
        ]
        if _raw is True:
            decode = _fake_decode
        else:
            decode = self._decode_message

        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            return await func(await decode(message))

        return wrapper

    def _wrap_parse_message(
        self, func: Callable[[PropanMessage], Awaitable[T]]
    ) -> Callable[[Any], Awaitable[T]]:
        @wraps(func)
        async def parse_wrapper(message: Any) -> T:
            return await func(await self._parse_message(message))

        return parse_wrapper

    def _log_execution(
        self,
        **broker_args: Any,
    ) -> Wrapper:
        def decor(
            func: Callable[[PropanMessage], Awaitable[T]]
        ) -> Callable[[PropanMessage], Awaitable[T]]:
            @wraps(func)
            async def log_wrapper(message: PropanMessage) -> T:
                log_context = self._get_log_context(message=message, **broker_args)

                with context.scope("log_context", log_context):
                    self._log("Received", extra=log_context)

                    try:
                        r = await func(message)
                    except SkipMessage as e:
                        self._log("Skipped", extra=log_context)
                        raise e
                    except Exception as e:
                        self._log(repr(e), logging.ERROR)
                        raise e
                    else:
                        self._log("Processed", extra=log_context)
                        return r

            return log_wrapper

        return decor

    def _log(
        self,
        message: str,
        log_level: Optional[int] = None,
        extra: Optional[AnyDict] = None,
    ) -> None:
        if self.logger is not None:
            self.logger.log(
                level=(log_level or self.log_level), msg=message, extra=extra
            )


async def _fake_decode(message: PropanMessage) -> PropanMessage:
    return message
