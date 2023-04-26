from abc import ABC, abstractmethod
from collections import Counter
from logging import Logger
from types import TracebackType
from typing import Callable, Optional, Type

from typing_extensions import Counter as CounterType

from propan.utils.functions import call_or_await


class BaseWatcher(ABC):
    max_tries: int

    def __init__(self, max_tries: int = 0, logger: Optional[Logger] = None):
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


class FakePushBackWatcher(BaseWatcher):
    def add(self, message_id: str) -> None:
        pass

    def is_max(self, message_id: str) -> bool:
        return False

    def remove(self, message_id: str) -> None:
        pass


class PushBackWatcher(BaseWatcher):
    memory: CounterType[str]

    def __init__(self, max_tries: int = 3, logger: Optional[Logger] = None):
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
        message_id: str,
        on_success: Callable[[], None] = lambda: None,
        on_max: Callable[[], None] = lambda: None,
        on_error: Callable[[], None] = lambda: None,
    ):
        self.watcher = watcher
        self.on_success = on_success
        self.on_max = on_max
        self.on_error = on_error
        self._message_id = message_id

    async def __aenter__(self) -> None:
        self.watcher.add(self._message_id)

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if not exc_type:
            await call_or_await(self.on_success)
            self.watcher.remove(self._message_id)

        elif self.watcher.is_max(self._message_id):
            await call_or_await(self.on_max)
            self.watcher.remove(self._message_id)

        else:
            await call_or_await(self.on_error)
