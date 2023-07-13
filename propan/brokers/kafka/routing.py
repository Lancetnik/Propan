from typing import Awaitable, Callable

from aiokafka.structs import ConsumerRecord

from propan.brokers._model.broker_usecase import HandlerCallable, T_HandlerReturn
from propan.brokers._model.routing import BrokerRouter
from propan.types import AnyDict


class KafkaRouter(BrokerRouter[ConsumerRecord]):
    def handle(  # type: ignore[override]
        self,
        *topics: str,
        **kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[ConsumerRecord, bool], Awaitable[T_HandlerReturn]],
    ]:
        return super().handle(*[self.prefix + t for t in topics], **kwargs)
