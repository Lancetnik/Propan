import logging
from functools import wraps
from typing import Awaitable, Callable, Optional, Tuple, TypeVar, Union, cast

from propan._compat import dump_json
from propan.brokers.constants import ContentType, ContentTypes
from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    PushBackWatcher,
)
from propan.types import SendableMessage
from propan.utils import context


def to_send(msg: SendableMessage) -> Tuple[bytes, Optional[ContentType]]:
    if msg is None:
        return b"", None

    if isinstance(msg, bytes):
        return msg, None

    if isinstance(msg, str):
        return msg.encode(), ContentTypes.text.value

    return (
        dump_json(msg).encode(),
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


MsgType = TypeVar("MsgType")
T_HandlerReturn = TypeVar("T_HandlerReturn")


def suppress_decor(
    func: Callable[
        [MsgType],
        Union[
            T_HandlerReturn,
            Awaitable[T_HandlerReturn],
        ],
    ],
    _is_sync: bool = False,
) -> Callable[[MsgType, bool], Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]]:
    if _is_sync:
        func = cast(Callable[[MsgType], T_HandlerReturn], func)

        @wraps(func)
        def wrapper(
            message: MsgType, reraise_exc: bool = False
        ) -> Optional[T_HandlerReturn]:
            try:
                return func(message)
            except Exception as e:
                if reraise_exc is True:
                    raise e
                return None

    else:
        func = cast(Callable[[MsgType], Awaitable[T_HandlerReturn]], func)

        @wraps(func)
        async def wrapper(
            message: MsgType, reraise_exc: bool = False
        ) -> Optional[T_HandlerReturn]:
            try:
                return await func(message)
            except Exception as e:
                if reraise_exc is True:
                    raise e
                return None

    return wrapper


def set_message_context(
    func: Callable[
        [MsgType],
        Union[
            T_HandlerReturn,
            Awaitable[T_HandlerReturn],
        ],
    ],
    _is_sync: bool = False,
) -> Callable[[MsgType], Union[T_HandlerReturn, Awaitable[T_HandlerReturn],]]:
    if _is_sync:
        func = cast(Callable[[MsgType], T_HandlerReturn], func)

        @wraps(func)
        def wrapper(message: MsgType) -> T_HandlerReturn:
            with context.scope("message", message):
                return func(message)

    else:
        func = cast(Callable[[MsgType], Awaitable[T_HandlerReturn]], func)

        @wraps(func)
        async def wrapper(message: MsgType) -> T_HandlerReturn:
            with context.scope("message", message):
                return await func(message)

    return wrapper
