from typing import Any, Dict, Optional

from pydantic import Field

from propan.broker.schemas import NameRequired
from propan.rabbit.shared.constants import ExchangeType
from propan.rabbit.shared.types import TimeoutType


class RabbitQueue(NameRequired):
    name: str = ""
    durable: bool = False
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    bind_arguments: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    routing_key: str = Field(default="", exclude=True)

    def __hash__(self) -> int:
        return sum(
            (
                hash(self.name),
                int(self.durable),
                int(self.exclusive),
                int(self.auto_delete),
            )
        )

    @property
    def routing(self) -> Optional[str]:
        return self.routing_key or self.name or None

    def __init__(
        self,
        name: str,
        durable: bool = False,
        exclusive: bool = False,
        passive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: TimeoutType = None,
        robust: bool = True,
        bind_arguments: Optional[Dict[str, Any]] = None,
        routing_key: str = "",
    ):
        super().__init__(
            name=name,
            durable=durable,
            exclusive=exclusive,
            bind_arguments=bind_arguments,
            routing_key=routing_key,
            robust=robust,
            passive=passive,
            auto_delete=auto_delete,
            arguments=arguments,
            timeout=timeout,
        )


class RabbitExchange(NameRequired):
    type: str = ExchangeType.DIRECT.value
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

    def __hash__(self) -> int:
        return sum(
            (
                hash(self.name),
                hash(self.type),
                int(self.durable),
                int(self.auto_delete),
            )
        )

    def __init__(
        self,
        name: str,
        type: ExchangeType = ExchangeType.DIRECT,
        durable: bool = False,
        auto_delete: bool = False,
        internal: bool = False,
        passive: bool = False,
        arguments: Optional[Dict[str, Any]] = None,
        timeout: TimeoutType = None,
        robust: bool = True,
        bind_to: Optional["RabbitExchange"] = None,
        bind_arguments: Optional[Dict[str, Any]] = None,
        routing_key: str = "",
    ):
        super().__init__(
            name=name,
            type=type.value,
            durable=durable,
            auto_delete=auto_delete,
            routing_key=routing_key,
            bind_to=bind_to,
            bind_arguments=bind_arguments,
            robust=robust,
            internal=internal,
            passive=passive,
            timeout=timeout,
            arguments=arguments,
        )


def get_routing_hash(
    queue: RabbitQueue,
    exchange: Optional[RabbitExchange] = None,
) -> int:
    return hash(queue) + hash(exchange or "")
