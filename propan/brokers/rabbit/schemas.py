from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from aio_pika.abc import ExchangeType, TimeoutType
from pydantic import Field

from propan.brokers._model.schemas import BaseHandler, NameRequired, Queue
from propan.types import AnyDict

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

    bind_to: Optional["RabbitExchange"] = Field(None, exclude=True)
    bind_arguments: Optional[Dict[str, Any]] = Field(None, exclude=True)
    routing_key: str = Field("", exclude=True)


@dataclass
class Handler(BaseHandler):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = field(default=None, kw_only=True)

    def get_schema(self) -> Tuple[str, AnyDict]:
        dependant = self.get_dependant()

        payload_type: str
        if not dependant.params:
            payload_type = "null"
        else:
            payload_type = "string"

        return self.callback.__name__, {
            "subscribe": {
                "description": self.description or self.callback.__doc__ or "",
                "message": {
                    "payload": {
                        "type": payload_type
                    }
                }
            }
        }
