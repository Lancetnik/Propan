from functools import wraps
from typing import Optional, TypeVar, Callable

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher

T = TypeVar("T")

class RedisProcess(BrokerAsyncUsecase):
    ...
    def _process_message(
            self,
            func: Callable[[PropanMessage], T],
            watcher: Optional[BaseWatcher],
        ) -> Callable[[PropanMessage], T]:
            @wraps(func)
            async def wrapper(message: PropanMessage) -> T:
                r = await func(message)
                if message.reply_to:
                    await self.publish(r or "", message.reply_to)
                return r

            return wrapper
