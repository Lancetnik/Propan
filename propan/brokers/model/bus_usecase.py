from logging import Logger
from time import perf_counter
from functools import wraps, partial
from typing import Protocol, Callable, Dict, Union, Optional

from propan.log import access_logger
from propan.utils import apply_types, use_context
from propan.utils.context import message as message_context, context
from propan.brokers.push_back_watcher import BaseWatcher, PushBackWatcher, FakePushBackWatcher


class BrokerUsecase(Protocol):
    logger: Logger
    handlers: Dict[str, Callable] = {}
    
    def __init__(self, *args, logger: Optional[Logger] = access_logger, **kwargs):
        self.logger = logger
        context.set_context("logger", logger)

    def connect(self):
        raise NotImplementedError()

    def init_channel(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        raise NotImplementedError()

    def publish_message(self, queue_name: str, message: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def _decode_message(self) -> Callable:
        raise NotImplementedError()

    def _process_message(self, func: Callable, watcher: Optional[BaseWatcher]) -> Callable:
        raise NotImplementedError()
    
    def _get_log_context(self, *kwargs) -> None:
        return None

    def handle(self, func: Callable, retry: Union[bool, int] = False, **broker_args) -> Callable:
        return self._wrap_handler(func, retry, **broker_args)

    def _wrap_handler(self,
                      func: Callable,
                      retry: Union[bool, int],
                      **broker_args) -> Callable:
        func = use_context(func)

        if self._is_apply_types:
            func = apply_types(func)

        func = self._wrap_decode_message(func)

        func = retry_proccess(partial(self._process_message, func), retry, self.logger)

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
                self.logger.info("Received")

                try:
                    r = await func(message)
                except Exception as e:
                    self.logger.error(repr(e))
                else:
                    self.logger.info(f"Processed by {(perf_counter() - start):.4f}")
                    return r
            return wrapper
        return decor


def retry_proccess(func: Callable, try_number: Union[bool, int] = True, logger: Logger = access_logger):
    if try_number is True:
        watcher = FakePushBackWatcher(logger=logger)
    elif try_number is False:
        watcher = None
    else:
        watcher = PushBackWatcher(logger=logger, max_tries=try_number)
    return func(watcher=watcher)


def _set_message_context(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(message) -> None:
        message_context.set(message)
        return await func(message)
    return wrapper
