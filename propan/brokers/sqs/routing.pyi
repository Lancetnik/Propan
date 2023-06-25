from typing import Optional, Sequence, Union

from fast_depends.dependencies import Depends

from propan.brokers._model.broker_usecase import CustomDecoder, CustomParser
from propan.brokers._model.routing import BrokerRouter
from propan.brokers.sqs.schema import SQSQueue
from propan.types import AnyDict, HandlerWrapper

class SQSRouter(BrokerRouter):
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, SQSQueue],
        *,
        wait_interval: int = 1,
        max_messages_number: int = 10,  # 1...10
        attributes: Sequence[str] = (),
        message_attributes: Sequence[str] = (),
        request_attempt_id: Optional[str] = None,
        visibility_timeout: int = 0,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: CustomDecoder[AnyDict] = None,
        parse_message: CustomParser[AnyDict] = None,
        description: str = "",
    ) -> HandlerWrapper: ...
