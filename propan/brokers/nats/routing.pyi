from typing import Sequence, Union

from fast_depends.dependencies import Depends
from nats.aio.msg import Msg

from propan.brokers._model.broker_usecase import CustomDecoder, CustomParser
from propan.brokers._model.routing import BrokerRouter
from propan.types import HandlerWrapper

class NatsRouter(BrokerRouter):
    def handle(  # type: ignore[override]
        self,
        subject: str,
        queue: str = "",
        *,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[Msg] = None,
        parse_message: CustomParser[Msg] = None,
        description: str = "",
    ) -> HandlerWrapper: ...
