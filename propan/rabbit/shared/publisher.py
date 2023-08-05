from abc import ABC
from dataclasses import dataclass, field
from typing import Optional

from typing_extensions import TypeAlias

from propan.broker.publisher import BasePublisher
from propan.rabbit.shared.schemas import BaseRMQInformation
from propan.rabbit.shared.types import TimeoutType
from propan.types import AnyDict


@dataclass
class ABCPublisher(ABC, BasePublisher, BaseRMQInformation):
    routing_key: str = ""
    mandatory: bool = True
    immediate: bool = False
    persist: bool = False
    timeout: TimeoutType = None
    reply_to: Optional[str] = None
    message_kwargs: AnyDict = field(default_factory={})


QueueName: TypeAlias = str
ExchangeName: TypeAlias = str
