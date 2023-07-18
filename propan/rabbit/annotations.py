from typing_extensions import Annotated

from propan.rabbit.broker import RabbitBroker as RB
from propan.rabbit.message import RabbitMessage as RM
from propan.utils.context import Context

RabbitMessage = Annotated[RM, Context("message")]
RabbitBroker = Annotated[RB, Context("broker")]
