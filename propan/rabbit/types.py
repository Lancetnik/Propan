from typing import Union

import aio_pika
from typing_extensions import TypeAlias

from propan.rabbit.shared.types import TimeoutType
from propan.rabbit.shared.wrapper import AMQPHandlerCallWrapper
from propan.types import SendableMessage

__all__ = (
    "TimeoutType",
    "AMQPHandlerCallWrapper",
    "AioPikaSendableMessage",
)

AioPikaSendableMessage: TypeAlias = Union[aio_pika.Message, SendableMessage]
