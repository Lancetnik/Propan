import json
import logging
from enum import Enum
from functools import wraps
from typing import Awaitable, Callable, Optional, Tuple, TypeVar, Union

from pydantic.json import pydantic_encoder
from typing_extensions import TypeAlias

from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    PushBackWatcher,
)
from propan.types import SendableMessage
from propan.utils import context

T = TypeVar("T")
P = TypeVar("P")

ContentType: TypeAlias = str


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"


def to_send(msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
    if msg is None:
        return b"", None

    if isinstance(msg, bytes):
        return msg, None

    if isinstance(msg, str):
        return msg.encode(), ContentTypes.text.value

    return (
        json.dumps(msg, default=pydantic_encoder).encode(),
        ContentTypes.json.value,
    )


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
    func: Callable[[T], Awaitable[P]]
) -> Callable[[T, bool], Awaitable[Optional[P]]]:
    @wraps(func)
    async def wrapper(message: T, reraise_exc: bool = False) -> Optional[P]:
        try:
            return await func(message)
        except Exception as e:
            if reraise_exc is True:
                raise e
            return None

    return wrapper


def set_message_context(
    func: Callable[[T], Awaitable[P]]
) -> Callable[[T], Awaitable[P]]:
    @wraps(func)
    async def wrapper(message: T) -> P:
        with context.scope("message", message):
            return await func(message)

    return wrapper
