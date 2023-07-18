from abc import ABC, abstractmethod
from collections import Counter
from logging import Logger
from types import TracebackType
from typing import Optional, Type

from typing_extensions import Counter as CounterType

from propan.broker.message import PropanMessage
from propan.broker.types import MsgType
from propan.exceptions import SkipMessage
from propan.types import AnyDict
from propan.utils.functions import call_or_await


class BaseWatcher(ABC):
    max_tries: int

    def __init__(
        self,
        max_tries: int = 0,
        logger: Optional[Logger] = None,
    ):
        self.logger = logger
        self.max_tries = max_tries

    @abstractmethod
    def add(self, message_id: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def is_max(self, message_id: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def remove(self, message_id: str) -> None:
        raise NotImplementedError()


class EndlessWatcher(BaseWatcher):
    def add(self, message_id: str) -> None:
        pass

    def is_max(self, message_id: str) -> bool:
        return False

    def remove(self, message_id: str) -> None:
        pass


class OneTryWatcher(BaseWatcher):
    def add(self, message_id: str) -> None:
        pass

    def is_max(self, message_id: str) -> bool:
        return True

    def remove(self, message_id: str) -> None:
        pass


class PushBackWatcher(BaseWatcher):
    memory: CounterType[str]

    def __init__(
        self,
        max_tries: int = 3,
        logger: Optional[Logger] = None,
    ):
        super().__init__(logger=logger, max_tries=max_tries)
        self.memory = Counter()

    def add(self, message_id: str) -> None:
        self.memory[message_id] += 1

    def is_max(self, message_id: str) -> bool:
        is_max = self.memory[message_id] > self.max_tries
        if self.logger is not None:
            if is_max:
                self.logger.error(f"Already retried {self.max_tries} times. Skipped.")
            else:
                self.logger.error("Error is occured. Pushing back to queue.")
        return is_max

    def remove(self, message: str) -> None:
        self.memory[message] = 0
        self.memory += Counter()


class WatcherContext:
    def __init__(
        self,
        watcher: BaseWatcher,
        message: PropanMessage[MsgType],
        **extra_args: AnyDict,
    ):
        self.watcher = watcher
        self.message = message
        self.extra_args = extra_args or {}

    async def __aenter__(self) -> None:
        self.watcher.add(self.message.message_id)

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if not exc_type:
            await call_or_await(self.message.ack, **self.extra_args)
            self.watcher.remove(self.message.message_id)

        elif isinstance(exc_val, SkipMessage):
            self.watcher.remove(self.message.nack)

        elif self.watcher.is_max(self.message.message_id):
            await call_or_await(self.message.reject, **self.extra_args)
            self.watcher.remove(self.message.message_id)

        else:
            await call_or_await(self.message.nack, **self.extra_args)
