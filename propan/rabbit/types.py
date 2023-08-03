from typing import Union

import aio_pika
from typing_extensions import TypeAlias

from propan.rabbit.shared.types import TimeoutType
from propan.types import SendableMessage

__all__ = (
    "TimeoutType",
    "AioPikaSendableMessage",
)

AioPikaSendableMessage: TypeAlias = Union[aio_pika.Message, SendableMessage]
