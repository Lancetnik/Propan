from typing_extensions import Annotated

from propan.annotations import ContextRepo, Logger, NoCast
from propan.rabbit.broker import RabbitBroker as RB
from propan.rabbit.message import RabbitMessage as RM
from propan.utils.context import Context

__all__ = (
    "Logger",
    "ContextRepo",
    "NoCast",
    "RabbitMessage",
    "RabbitBroker",
)

RabbitMessage = Annotated[RM, Context("message")]
RabbitBroker = Annotated[RB, Context("broker")]
