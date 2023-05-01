from typing import Any, Dict, Optional

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

    routing_key: str = Field(default="", exclude=True)


class RabbitExchange(NameRequired):
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True


class Handler(BaseModel):
    callback: DecoratedCallable
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None
