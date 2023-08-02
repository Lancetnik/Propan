from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from unittest.mock import MagicMock

from typing_extensions import TypeAlias

from propan.broker.schemas import HandlerCallWrapper
from propan.broker.schemas import Publisher as BasePub
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
from propan.types import AnyDict


@dataclass
class Publisher(ABC, BasePub):
    queue: RabbitQueue = field(default=RabbitQueue(""))
    exchange: Optional[RabbitExchange] = None
    routing_key: str = ""
    mandatory: bool = True
    immediate: bool = False
    persist: bool = False
    timeout: TimeoutType = None
    reply_to: Optional[str] = None
    message_kwargs: AnyDict = field(default_factory={})


QueueName: TypeAlias = str
ExchangeName: TypeAlias = str


class AMQPHandlerCallWrapper(HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]):
    response_mocks: Dict[
        ExchangeName,
        Dict[
            QueueName,
            MagicMock,
        ],
    ]

    _publishers: List[Publisher]
