from typing import Sequence

from fast_depends.dependencies import Depends

from propan.brokers._model.broker_usecase import CustomDecoder, CustomParser
from propan.brokers._model.routing import BrokerRouter
from propan.types import AnyDict, HandlerWrapper

class RedisRouter(BrokerRouter):
    def handle(  # type: ignore[override]
        self,
        channel: str,
        *,
        pattern: bool = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[AnyDict] = None,
        parse_message: CustomParser[AnyDict] = None,
        description: str = "",
    ) -> HandlerWrapper: ...
