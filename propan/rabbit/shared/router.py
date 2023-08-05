from typing import Any, Callable, Union

from aio_pika.message import IncomingMessage

from propan._compat import model_copy
from propan.broker.router import BrokerRouter
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.broker.wrapper import HandlerCallWrapper
from propan.rabbit.shared.schemas import RabbitQueue
from propan.types import AnyDict


class RabbitRouter(BrokerRouter[IncomingMessage]):
    def subscriber(
        self,
        queue: Union[str, RabbitQueue],
        *broker_args: Any,
        **broker_kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        HandlerCallWrapper[IncomingMessage, P_HandlerParams, T_HandlerReturn],
    ]:
        q = RabbitQueue.validate(queue)
        new_q = model_copy(q, update={"name": self.prefix + q.name})
        return self._wrap_subscriber(new_q, *broker_args, **broker_kwargs)
