from typing import Any, Callable, Optional, TypeVar

from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import HandlerWrapper, SendableMessage


T = TypeVar("T")


class MyBroker(BrokerUsecase):
    async def _connect(self, *args: Any, **kwargs: Any) -> Any:
        pass

    async def close(self) -> None:
        pass

    def handle(self, *args: Any, **kwargs: Any) -> HandlerWrapper:
        pass

    async def start(self) -> None:
        pass

    async def _parse_message(self, message: Any) -> PropanMessage:
        pass

    async def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]:
        pass

    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: Any,
    ) -> Any:
        pass
