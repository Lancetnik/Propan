from typing import Callable

from aiokafka import ConsumerRecord

from propan.broker.router import BrokerRouter
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.broker.wrapper import HandlerCallWrapper
from propan.types import AnyDict


class KafkaRouter(BrokerRouter[ConsumerRecord]):
    def subscriber(
        self,
        *topics: str,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[ConsumerRecord, P_HandlerParams, T_HandlerReturn],
    ]:
        return self._wrap_subscriber(
            *(self.prefix + x for x in topics),
            **broker_kwargs,
        )
