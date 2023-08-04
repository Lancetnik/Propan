import re
import sys
from contextlib import asynccontextmanager
from types import MethodType
from typing import Any, Optional, Union

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock
from uuid import uuid4

import aiormq
from aio_pika.message import IncomingMessage
from pamqp import commands as spec
from pamqp.header import ContentHeader

from propan.brokers.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from propan.brokers.rabbit.rabbit_broker import PikaSendableMessage, TimeoutType
from propan.brokers.rabbit.utils import validate_exchange, validate_queue
from propan.test.utils import call_handler
from propan.types import AnyDict

__all__ = (
    "build_message",
    "TestRabbitBroker",
)


class PatchedMessage(IncomingMessage):
    @asynccontextmanager
    async def process(self):  # type: ignore
        yield

    async def ack(self, multiple: bool = False) -> None:
        pass

    async def nack(self, multiple: bool = False, requeue: bool = True) -> None:
        pass

    async def reject(self, requeue: bool = False) -> None:
        pass


def build_message(
    message: PikaSendableMessage = "",
    queue: Union[RabbitQueue, str] = "",
    exchange: Union[RabbitExchange, str, None] = None,
    *,
    routing_key: str = "",
    **message_kwargs: AnyDict,
) -> PatchedMessage:
    que, exch = validate_queue(queue), validate_exchange(exchange)
    msg = RabbitBroker._validate_message(message, None, **message_kwargs)

    routing = routing_key or (que.name if que else "")

    return PatchedMessage(
        aiormq.abc.DeliveredMessage(
            delivery=spec.Basic.Deliver(
                exchange=exch.name if exch else "",
                routing_key=routing,
            ),
            header=ContentHeader(
                properties=spec.Basic.Properties(
                    content_type=msg.content_type,
                    message_id=str(uuid4()),
                    headers=msg.headers,
                )
            ),
            body=msg.body,
            channel=AsyncMock(),
        )
    )


async def publish(
    self: RabbitBroker,
    message: PikaSendableMessage = "",
    queue: Union[RabbitQueue, str] = "",
    exchange: Union[RabbitExchange, str, None] = None,
    *,
    routing_key: str = "",
    mandatory: bool = True,
    immediate: bool = False,
    timeout: TimeoutType = None,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
    **message_kwargs: AnyDict,
) -> Any:
    exch = validate_exchange(exchange)

    incoming = build_message(
        message=message,
        queue=queue,
        exchange=exch,
        routing_key=routing_key,
        **message_kwargs,
    )

    for handler in self.handlers:  # pragma: no branch
        if handler.exchange == exch:
            call = False

            if exch is None or handler.exchange.type == ExchangeType.DIRECT:
                call = handler.queue.name == incoming.routing_key

            elif handler.exchange.type == ExchangeType.FANOUT:
                call = True

            elif handler.exchange.type == ExchangeType.TOPIC:
                call = re.match(
                    handler.queue.name.replace(".", r"\.").replace("*", ".*"),
                    incoming.routing_key,
                )

            elif handler.exchange.type == ExchangeType.HEADERS:
                queue_headers = handler.queue.bind_arguments
                msg_headers = incoming.headers

                if not queue_headers and not msg_headers:
                    call = True

                else:
                    matcher = queue_headers.pop("x-match", "all")

                    full = True
                    none = True
                    for k, v in queue_headers.items():
                        if msg_headers.get(k) != v:
                            full = False
                        else:
                            none = False

                    if not none:
                        call = matcher == "any" or full

            if call:
                r = await call_handler(
                    handler,
                    incoming,
                    callback,
                    callback_timeout,
                    raise_timeout,
                )
                if callback:  # pragma: no branch
                    return r


def TestRabbitBroker(broker: RabbitBroker) -> RabbitBroker:
    broker._channel = AsyncMock()
    broker.connect = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
