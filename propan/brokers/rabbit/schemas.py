from typing import Any, Dict, Optional, Union

from aio_pika.abc import ExchangeType, TimeoutType
from pydantic import BaseModel, Field

from propan.brokers.model.schemas import NameRequired, Queue
from propan.types import DecoratedCallable

__all__ = (
    "RabbitQueue",
    "RabbitExchange",
    "Handler",
    "ExchangeType",
)


class RabbitQueue(Queue):
    durable: bool = False
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    declare: bool = Field(default=True, exclude=True)
    routing_key: str = Field(default="", exclude=True)


class RabbitExchange(NameRequired):
    type: Union[ExchangeType, str] = ExchangeType.DIRECT
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    declare: bool = Field(default=True, exclude=True)


class Handler(BaseModel):
    callback: DecoratedCallable
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None
