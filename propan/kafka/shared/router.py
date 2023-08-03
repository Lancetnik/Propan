from typing import Callable

from aiokafka import ConsumerRecord

from propan.broker.router import BrokerRouter, P_RouteCall, T_RouteReturn
from propan.broker.schemas import HandlerCallWrapper
from propan.types import AnyDict


class KafkaRouter(BrokerRouter[ConsumerRecord]):
    def subscriber(
        self,
        *topics: str,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        HandlerCallWrapper[P_RouteCall, T_RouteReturn],
    ]:
        return self._wrap_subscriber(
            *(self.prefix + x for x in topics),
            **broker_kwargs,
        )
