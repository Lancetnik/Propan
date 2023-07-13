from typing import Any, Awaitable, Callable, Union

from aio_pika.message import IncomingMessage

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
        queue = validate_queue(queue)
        queue.name = self.prefix + queue.name
        return super().handle(queue, *args, **kwargs)
