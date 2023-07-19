from typing import Any, Awaitable, Callable

from nats.aio.msg import Msg

from propan.brokers._model.broker_usecase import HandlerCallable, T_HandlerReturn
from propan.brokers._model.routing import BrokerRouter
from propan.types import AnyDict


class NatsRouter(BrokerRouter[Msg]):
    def handle(
        self,
        subject: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Msg, bool], Awaitable[T_HandlerReturn]],
    ]:
        return super().handle(self.prefix + subject, *args, **kwargs)
