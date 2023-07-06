from types import TracebackType
from typing import Generic, Optional, Type

from typing_extensions import TypeVar

from propan.brokers._model.schemas import PropanMessage

MsgType = TypeVar("MsgType")


class BaseMiddleware(Generic[MsgType]):
    message: PropanMessage[MsgType]

    def __init__(self, msg: PropanMessage[MsgType]) -> None:
        self.message = msg

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ):
        pass
