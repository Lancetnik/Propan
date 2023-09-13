from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, Dict, Optional, Union

from fast_depends.core import CallModel
from pydantic import Field
from typing_extensions import TypeAlias

from propan.asyncapi.bindings import (
    AsyncAPIChannelBinding,
    AsyncAPIOperationBinding,
    amqp,
)
from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.message import AsyncAPICorrelationId, AsyncAPIMessage
from propan.asyncapi.subscription import AsyncAPISubscription
from propan.brokers._model.schemas import BaseHandler, NameRequired, Queue
from propan.types import AnyDict, DecoratedCallable


@unique
class ExchangeType(str, Enum):
    FANOUT = "fanout"
    DIRECT = "direct"
    TOPIC = "topic"
    HEADERS = "headers"
    X_DELAYED_MESSAGE = "x-delayed-message"
    X_CONSISTENT_HASH = "x-consistent-hash"
    X_MODULUS_HASH = "x-modulus-hash"


TimeoutType: TypeAlias = Optional[Union[int, float]]


class RabbitQueue(Queue):
    name: str = ""
    durable: bool = False
    exclusive: bool = False
    passive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None
    timeout: TimeoutType = None
    robust: bool = True

    bind_arguments: Optional[Dict[str, Any]] = None
    routing_key: str = ""

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

    bind_to: Optional["RabbitExchange"] = None
    bind_arguments: Optional[Dict[str, Any]] = None
    routing_key: str = Field(default="")

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


@dataclass
class Handler(BaseHandler):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = field(default=None)
    consume_arguments: AnyDict = field(default_factory=dict)

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: CallModel,
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
        consume_arguments: Optional[AnyDict] = None,
        _description: str = "",
    ):
        self.callback = callback
        self.dependant = dependant
        self.queue = queue
        self.exchange = exchange
        self._description = _description
        self.consume_arguments = consume_arguments or {}

    def get_schema(self) -> Dict[str, AsyncAPIChannel]:
        message_title, body, reply_to = self.get_message_object()

        return {
            self.title: AsyncAPIChannel(
                subscribe=AsyncAPISubscription(
                    description=self.description,
                    bindings=AsyncAPIOperationBinding(
                        amqp=amqp.AsyncAPIAmqpOperationBinding(
                            cc=None
                            if (
                                self.exchange
                                and self.exchange.type
                                in (
                                    ExchangeType.FANOUT.value,
                                    ExchangeType.HEADERS.value,
                                )
                            )
                            else self.queue.name,
                            replyTo=reply_to,
                        ),
                    ),
                    message=AsyncAPIMessage(
                        title=message_title,
                        payload=body,
                        correlationId=AsyncAPICorrelationId(
                            location="$message.header#/correlation_id"
                        ),
                    ),
                ),
                bindings=AsyncAPIChannelBinding(
                    amqp=amqp.AsyncAPIAmqpChannelBinding(
                        **{
                            "is": "routingKey",  # type: ignore
                            "queue": None
                            if (
                                self.exchange
                                and self.exchange.type
                                in (
                                    ExchangeType.FANOUT.value,
                                    ExchangeType.HEADERS.value,
                                )
                            )
                            else amqp.AsyncAPIAmqpQueue(
                                name=self.queue.name,
                                durable=self.queue.durable,
                                exclusive=self.queue.exclusive,
                                autoDelete=self.queue.auto_delete,
                            ),
                            "exchange": (
                                amqp.AsyncAPIAmqpExchange(type="default")
                                if self.exchange is None
                                else amqp.AsyncAPIAmqpExchange(
                                    type=self.exchange.type,  # type: ignore
                                    name=self.exchange.name,
                                    durable=self.exchange.durable,
                                    autoDelete=self.exchange.auto_delete,
                                )
                            ),
                        }
                    )
                ),
            ),
        }
