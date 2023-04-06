import logging
from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Optional, Union

from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    PushBackWatcher,
)
from propan.log import access_logger
from propan.utils import apply_types, use_context
from propan.utils.context import context
from propan.utils.context import message as message_context


class BrokerUsecase(ABC):
    logger: logging.Logger
    log_level: int
    _fmt: str = "%(asctime)s %(levelname)s - %(message)s"

    def __init__(
        self,
        *args,
        apply_types: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        **kwargs,
    ):
        self.logger = logger
        self.log_level = log_level

        self._is_apply_types = apply_types
        self._connection_args = args
        self._connection_kwargs = kwargs

        context.set_context("logger", logger)
        context.set_context("broker", self)

    async def connect(self, *args, **kwargs):
        if self._connection is None:
            _args = args or self._connection_args
            _kwargs = kwargs or self._connection_kwargs
            self._connection = await self._connect(*_args, **_kwargs)
            return self._connection

    @abstractmethod
    async def _connect(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def publish_message(self, queue_name: str, message: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _decode_message(self) -> Union[str, dict]:
        raise NotImplementedError()

    @abstractmethod
    def _process_message(
        self, func: Callable, watcher: Optional[BaseWatcher]
    ) -> Callable:
        raise NotImplementedError()

    async def start(self) -> None:
        self._init_logger()
        await self.connect()

    def _get_log_context(self, *kwargs) -> dict[str, Any]:
        return {}

    def handle(
        self, func: Callable, retry: Union[bool, int] = False, **broker_args
    ) -> Callable:
        return self._wrap_handler(func, retry, **broker_args)

    @property
    def fmt(self):
        return self._fmt

    def _init_logger(self):
        for handler in self.logger.handlers:
            handler.setFormatter(type(handler.formatter)(self.fmt))

    async def __aenter__(self) -> "BrokerUsecase":
        await self.connect()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    def _wrap_handler(
        self, func: Callable, retry: Union[bool, int], **broker_args
    ) -> Callable:
        func = use_context(func)

        if self._is_apply_types:
            func = apply_types(func)

        func = self._wrap_decode_message(func)

        func = self._process_message(func, _get_watcher(self.logger, retry))

        if self.logger is not None:
            func = self._log_execution(**broker_args)(func)

        func = _set_message_context(func)

        return func

    def _wrap_decode_message(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message) -> None:
            return await func(await self._decode_message(message))

        return wrapper

    def _log_execution(self, **broker_args):
        def decor(func):
            @wraps(func)
            async def wrapper(message):
                start = perf_counter()

                self._get_log_context(message=message, **broker_args)
                self.logger.log(self.log_level, "Received")

                try:
                    r = await func(message)
                except Exception as e:
                    self.logger.error(repr(e))
                else:
                    self.logger.log(
                        self.log_level, f"Processed by {(perf_counter() - start):.4f}"
                    )
                    return r

            return wrapper

        return decor


def _get_watcher(
    logger: logging.Logger, try_number: Union[bool, int] = True
) -> Optional[BaseWatcher]:
    if try_number is True:
        watcher = FakePushBackWatcher(logger=logger)
    elif try_number is False:
        watcher = None
    else:
        watcher = PushBackWatcher(logger=logger, max_tries=try_number)
    return watcher


def _set_message_context(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(message) -> None:
        message_context.set(message)
        return await func(message)

    return wrapper
