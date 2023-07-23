from typing import Awaitable, Callable, Union

from propan._compat import model_copy
from propan.brokers._model.broker_usecase import HandlerCallable, T_HandlerReturn
from propan.brokers._model.routing import BrokerRouter
from propan.brokers.sqs.schema import SQSQueue
from propan.types import AnyDict


class SQSRouter(BrokerRouter[AnyDict]):
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, SQSQueue],
        **kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]:
        if isinstance(queue, str):
            queue = SQSQueue(queue)

        return super().handle(
            model_copy(queue, update={"name": self.prefix + queue.name}), **kwargs
        )
