from dataclasses import dataclass
from typing import List, Union, Optional

from propan.types import HandlerWrapper, HandlerCallable
from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import BaseHandler
from propan.brokers.rabbit import RabbitExchange, RabbitQueue


@dataclass
class Handler(BaseHandler):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None


class RabbitBroker(BrokerUsecase):
    handlers: List[Handler]

    def handle(
        self,
        queue: RabbitQueue,
        exchange: Union[RabbitExchange, None] = None,
        *,
        retry: Union[bool, int] = False,
    ) -> HandlerWrapper:

        def wrapper(func: HandlerCallable) -> HandlerCallable:
            func = self._wrap_handler(func, retry=retry)
            handler = Handler(callback=func, queue=queue, exchange=exchange)
            self.handlers.append(handler)

            return func

        return wrapper