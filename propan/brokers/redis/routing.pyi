from typing import Awaitable, Callable, Sequence

from fast_depends.dependencies import Depends

from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.routing import BrokerRouter
from propan.types import AnyDict

class RedisRouter(BrokerRouter[AnyDict]):
    def handle(  # type: ignore[override]
        self,
        channel: str,
        *,
        pattern: bool = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]: ...
