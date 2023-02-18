from typing import Optional, Dict, Any, Callable, Optional, Union

from aio_pika.abc import TimeoutType, ExchangeType
from pydantic import BaseModel

from propan.brokers.model.schemas import Queue, NameRequired


class RabbitQueue(Queue):
    durable: bool = False
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True


class RabbitExchange(NameRequired):
    type: Union[ExchangeType, str] = ExchangeType.DIRECT
    durable: bool = False
    auto_delete: bool = False
    internal: bool = False
    passive: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True


class Handler(BaseModel):
    callback: Callable
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = None
