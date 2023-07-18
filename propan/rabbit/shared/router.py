from typing import Any, Callable, Union

from aio_pika.message import IncomingMessage

from propan.broker.router import BrokerRouter, P_RouteCall, T_RouteReturn
from propan.rabbit.shared.schemas import RabbitQueue
from propan.types import AnyDict


class RabbitRouter(BrokerRouter[IncomingMessage]):
    def subscriber(
        self,
        queue: Union[str, RabbitQueue],
        *broker_args: Any,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        Callable[[IncomingMessage, bool], T_RouteReturn],
    ]:
        q = RabbitQueue.validate(queue)
        q.name = self.prefix + q.name

        return self._wrap_subscriber(q, *broker_args, **broker_kwargs)
