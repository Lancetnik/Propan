from typing import Awaitable, Callable, Sequence, Union

from fast_depends.dependencies import Depends
from nats.aio.msg import Msg

from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.routing import BrokerRouter

class NatsRouter(BrokerRouter[Msg]):
    def handle(  # type: ignore[override]
        self,
        subject: str,
        queue: str = "",
        *,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[Msg] = None,
        parse_message: AsyncParser[Msg] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Msg, bool], Awaitable[T_HandlerReturn]],
    ]: ...
