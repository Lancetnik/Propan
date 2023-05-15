import sys
from contextlib import asynccontextmanager
from types import MethodType
from typing import Any, Optional, Union

from propan.types import AnyDict

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
from propan.brokers.rabbit.rabbit_broker import (  # type: ignore
    PikaSendableMessage,
    TimeoutType,
    _validate_exchange,
    _validate_queue,
)
from propan.test.utils import call_handler

__all__ = (
    "build_message",
    "TestRabbitBroker",
)


class PatchedMessage(IncomingMessage):
    @asynccontextmanager
    async def process(self):  # type: ignore
        yield


def build_message(
    message: PikaSendableMessage = "",
    queue: Union[RabbitQueue, str] = "",
    exchange: Union[RabbitExchange, str, None] = None,
    *,
    routing_key: str = "",
    **message_kwargs: AnyDict,
) -> PatchedMessage:
    que, exch = _validate_queue(queue), _validate_exchange(exchange)
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
    incoming = build_message(
        message=message,
        queue=queue,
        exchange=exchange,
        routing_key=routing_key,
        **message_kwargs,
    )

    for handler in self.handlers:  # pragma: no branch
        if not handler.exchange:
            if not exchange:  # pragma: no branch
                if handler.queue.name == incoming.routing_key:
                    r = await call_handler(
                        handler, incoming, callback, callback_timeout, raise_timeout
                    )
                    if callback:  # pragma: no branch
                        return r

        elif (  # pragma: no branch
            handler.exchange.type == ExchangeType.DIRECT
            or handler.exchange.type == ExchangeType.TOPIC
        ):
            if handler.queue.name == incoming.routing_key:
                r = await call_handler(
                    handler, incoming, callback, callback_timeout, raise_timeout
                )
                if callback:
                    return r

        elif handler.exchange.type == ExchangeType.FANOUT:
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:
                return r


def TestRabbitBroker(broker: RabbitBroker) -> RabbitBroker:
    broker._channel = AsyncMock()
    broker.connect = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
