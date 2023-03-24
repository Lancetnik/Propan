from functools import wraps, partial
from logging import Logger
from time import monotonic
from typing import Protocol, Callable, Dict, Union, Optional

from propan.log import logger

from propan.brokers.push_back_watcher import BaseWatcher, PushBackWatcher, FakePushBackWatcher

from propan.utils.context import message as message_context
from propan.utils import apply_types, use_context


class BrokerUsecase(Protocol):
    handlers: Dict[str, Callable] = {}

    def connect(self):
        raise NotImplementedError()

    def init_channel(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        raise NotImplementedError()

    def handle(self, func: Callable, retry: Union[bool, int] = False, **broker_args) -> Callable:
        return self._wrap_handler(func, retry)

    def publish_message(self, queue_name: str, message: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()

    def _decode_message(self) -> Callable:
        raise NotImplementedError()

    def _process_message(self, func: Callable, watcher: Optional[BaseWatcher]) -> Callable:
        raise NotImplementedError()

    def _wrap_handler(self,
                      func: Callable,
                      retry: Union[bool, int]) -> Callable:
        func = use_context(func)

        if self._is_apply_types:
            func = apply_types(func)

        func = self._decode_message(func)

        func = retry_proccess(
            partial(self._process_message, func), retry, self.logger)

        func = _log_execution(self.logger)(func)

        func = _set_message_context(func)

        return func


def retry_proccess(func: Callable, try_number: Union[bool, int] = True, logger: Logger = logger):
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


def _log_execution(logger):
    def decor(func):
        @wraps(func)
        async def wrapper(message):
            start = monotonic()
            logger.info(f"Received with '{message.body.decode()}'")

            try:
                return await func(message)
            finally:
                logger.info(f"Processed in {monotonic() - start}")
        return wrapper
    return decor
