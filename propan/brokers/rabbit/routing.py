from typing import Any, Awaitable, Callable, Union

from aio_pika.message import IncomingMessage

from propan._compat import model_copy
from propan.brokers._model.broker_usecase import HandlerCallable, T_HandlerReturn
from propan.brokers._model.routing import BrokerRouter
from propan.brokers.rabbit.schemas import RabbitQueue
from propan.brokers.rabbit.utils import validate_queue
from propan.types import AnyDict


class RabbitRouter(BrokerRouter[IncomingMessage]):
    def handle(
        self,
        queue: Union[str, RabbitQueue],
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[IncomingMessage, bool], Awaitable[T_HandlerReturn]],
    ]:
        q = validate_queue(queue)
        return super().handle(
            model_copy(q, update={"name": self.prefix + q.name}), *args, **kwargs
        )
