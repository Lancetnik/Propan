from typing import Dict, List
from unittest.mock import MagicMock

from typing_extensions import TypeAlias

from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.rabbit.shared.publisher import Publisher

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
