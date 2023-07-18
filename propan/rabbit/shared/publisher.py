from dataclasses import dataclass, field
from typing import Optional, Union

from propan.broker.publisher import BasePublisher
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.types import AnyDict


@dataclass
class Publisher(BasePublisher):
    queue: RabbitQueue = ""
    exchange: Union[RabbitExchange, str] = ("default",)
    routing_key: str = ("",)
    mandatory: bool = (True,)
    immediate: bool = (False,)
    persist: bool = (False,)
    reply_to: Optional[str] = (None,)
    message_kwargs: AnyDict = field(default_factory=dict)
