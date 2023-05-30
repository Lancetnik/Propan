from dataclasses import dataclass
from typing import Any, Dict, Optional

from aio_pika.abc import ExchangeType, TimeoutType
from pydantic import Field

from propan.brokers._model.schemas import BaseHandler, NameRequired, Queue

__all__ = (
    "RabbitQueue",
    "RabbitExchange",
    "Handler",
    "ExchangeType",
)


class RabbitQueue(Queue):
    name: str = ""
    durable: bool = False
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    bind_arguments: Optional[Dict[str, Any]] = Field(None, exclude=True)
    routing_key: str = Field("", exclude=True)

    @property
    def routing(self) -> Optional[str]:
        return self.routing_key or self.name or None


class RabbitExchange(NameRequired):
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    bind_to: Optional["RabbitExchange"] = Field(default=None, exclude=True)
    bind_arguments: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    routing_key: str = Field(default="", exclude=True)


@dataclass
class Handler(BaseHandler):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None
