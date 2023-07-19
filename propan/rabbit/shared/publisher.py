from dataclasses import dataclass, field
from typing import Optional

from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
from propan.types import AnyDict


@dataclass(slots=True)
class Publisher:
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None
    routing_key: str = ""
    mandatory: bool = True
    immediate: bool = False
    persist: bool = False
    timeout: TimeoutType = None
    reply_to: Optional[str] = None
    message_kwargs: AnyDict = field(default_factory={})
