from functools import wraps
from typing import Optional, TypeVar, Callable

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext

T = TypeVar("T")

class RabbitBroker(BrokerAsyncUsecase):
    ...
    def _process_message(
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher]
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            pika_message = message.raw_message
            if watcher is None:
                context = pika_message.process()
            else:
                context = WatcherContext(
                    watcher,
                    message,
                    on_success=pika_message.ack,
                    on_error=pika_message.nack,
                    on_max=pika_message.reject,
                )

            async with context:
                r = await func(message)
                if message.reply_to:
                    await self.publish(
                        message=r,
                        routing_key=message.reply_to,
                        correlation_id=pika_message.correlation_id,
                    )

                return r

        return wrapper