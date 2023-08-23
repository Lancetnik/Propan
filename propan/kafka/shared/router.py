from typing import Any, Callable, Sequence

from aiokafka import ConsumerRecord

from propan.broker.router import BrokerRoute as KafkaRoute
from propan.broker.router import BrokerRouter
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.broker.wrapper import HandlerCallWrapper
from propan.types import SendableMessage

__all__ = (
    "BrokerRouter",
    "KafkaRoute",
)


class KafkaRouter(BrokerRouter[str, ConsumerRecord]):
    def __init__(
        self,
        prefix: str = "",
        handlers: Sequence[KafkaRoute[ConsumerRecord, SendableMessage]] = (),
    ):
        for h in handlers:
            h.args = tuple(prefix + x for x in h.args)
        super().__init__(prefix, handlers)

    def subscriber(
        self,
        *topics: str,
        **broker_kwargs: Any,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[ConsumerRecord, P_HandlerParams, T_HandlerReturn],
    ]:
        return self._wrap_subscriber(
            *(self.prefix + x for x in topics),
            **broker_kwargs,
        )
