import logging
from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter
from typing import Any, Dict, List, Optional, Union

from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    PushBackWatcher,
)
from propan.log import access_logger
from propan.types import (
    AnyCallable,
    DecodedMessage,
    DecoratedAsync,
    DecoratedCallable,
    Wrapper,
)
from propan.utils import apply_types, context
from propan.utils.functions import to_async


class BrokerUsecase(ABC):
    logger: Optional[logging.Logger]
    log_level: int
    handlers: List[Any]
    _connection: Any
    _fmt: str

    def __init__(
        self,
        *args: Any,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: str = "%(asctime)s %(levelname)s - %(message)s",
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
        message: Any,
        *args: Any,
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError()

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def _decode_message(self, message: Any) -> DecodedMessage:
        raise NotImplementedError()

    @abstractmethod
    def _process_message(
        self, func: DecoratedCallable, watcher: Optional[BaseWatcher]
    ) -> Wrapper:
        raise NotImplementedError()

    async def start(self) -> None:
        if self.logger is not None:
            self._init_logger(self.logger)
        await self.connect()

    def _get_log_context(self, **kwargs: Any) -> Dict[str, Any]:
        return {}

    @abstractmethod
    def handle(
        self,
        *broker_args: Any,
        retry: Union[bool, int] = False,
        **broker_kwargs: Any,
    ) -> Wrapper:
        raise NotImplementedError()

    @property
    def fmt(self) -> str:
        return self._fmt

    def _init_logger(self, logger: logging.Logger) -> None:
        for handler in logger.handlers:
            formatter = handler.formatter
            if formatter is not None:
                use_colors = getattr(formatter, "use_colors", None)
                if use_colors is not None:
                    kwargs = {"use_colors": use_colors}
                else:
                    kwargs = {}
                handler.setFormatter(type(formatter)(self.fmt, **kwargs))

    async def __aenter__(self) -> "BrokerUsecase":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()

    def _wrap_handler(
        self, func: AnyCallable, retry: Union[bool, int], **broker_args: Any
    ) -> DecoratedAsync:
        func = to_async(func)

        if self._is_apply_types is True:
            func = apply_types(func)

        if self.logger is not None:
            func = self._log_execution(self.logger, **broker_args)(func)

        func = self._wrap_decode_message(func)

        func = self._process_message(func, _get_watcher(self.logger, retry))

        func = _set_message_context(func)

        func = suppress(func)

        return func

    def _wrap_decode_message(self, func: AnyCallable) -> DecoratedCallable:
        @wraps(func)
        async def wrapper(message: Any) -> Any:
            return await func(await self._decode_message(message))

        return wrapper

    def _log_execution(self, logger: logging.Logger, **broker_args: Any) -> Wrapper:
        def decor(func: AnyCallable) -> DecoratedCallable:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                message = context.get("message")

                start = perf_counter()

                log_context = self._get_log_context(message=message, **broker_args)

                with context.scope("log_context", log_context):
                    logger.log(self.log_level, "Received")

                    try:
                        r = await func(*args, **kwargs)
                    except Exception as e:
                        logger.error(repr(e))
                        raise e
                    else:
                        logger.log(
                            self.log_level,
                            f"Processed by {(perf_counter() - start):.4f}",
                        )
                        return r

            return wrapper

        return decor

    def _log(self, message: str, log_level: Optional[int] = None) -> None:
        if self.logger is not None:
            self.logger.log(level=(log_level or self.log_level), msg=message)


def _get_watcher(
    logger: Optional[logging.Logger], try_number: Union[bool, int] = True
) -> Optional[BaseWatcher]:
    watcher: Optional[BaseWatcher]
    if try_number is True:
        watcher = FakePushBackWatcher()
    elif try_number is False:
        watcher = None
    else:
        watcher = PushBackWatcher(logger=logger, max_tries=try_number)
    return watcher


def _set_message_context(func: AnyCallable) -> DecoratedCallable:
    @wraps(func)
    async def wrapper(message: Any) -> Any:
        with context.scope("message", message):
            return await func(message)

    return wrapper


def suppress(func: AnyCallable) -> DecoratedCallable:
    @wraps(func)
    async def wrapper(message: Any) -> Any:
        try:
            return await func(message)
        except Exception:
            pass

    return wrapper
