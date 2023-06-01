import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union

from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    PushBackWatcher,
)
from propan.utils import context

T = TypeVar("T")


def change_logger_handlers(logger: logging.Logger, fmt: str) -> None:
    for handler in logger.handlers:
        formatter = handler.formatter
        if formatter is not None:
            use_colors = getattr(formatter, "use_colors", None)
            if use_colors is not None:
                kwargs = {"use_colors": use_colors}
            else:
                kwargs = {}
            handler.setFormatter(type(formatter)(fmt, **kwargs))


def get_watcher(
    logger: Optional[logging.Logger],
    try_number: Union[bool, int] = True,
) -> Optional[BaseWatcher]:
    watcher: Optional[BaseWatcher]
    if try_number is True:
        watcher = FakePushBackWatcher()
    elif try_number is False:
        watcher = None
    else:
        watcher = PushBackWatcher(logger=logger, max_tries=try_number)
    return watcher


def suppress_decor(
    func: Callable[[Any], Awaitable[T]]
) -> Callable[[Any], Awaitable[Optional[T]]]:
    @wraps(func)
    async def wrapper(message: Any, reraise_exc: bool = False) -> Optional[T]:
        try:
            return await func(message)
        except Exception as e:
            if reraise_exc is True:
                raise e
            return None

    return wrapper


def set_message_context(
    func: Callable[[Any], Awaitable[T]]
) -> Callable[[Any], Awaitable[T]]:
    @wraps(func)
    async def wrapper(message: Any) -> T:
        with context.scope("message", message):
            return await func(message)

    return wrapper
