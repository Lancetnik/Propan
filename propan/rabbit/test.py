import re
import sys
from contextlib import asynccontextmanager
from functools import partial
from types import MethodType
from typing import Any, Dict, Optional, Union
from unittest.mock import MagicMock

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
from typing_extensions import assert_never

from propan.broker.test import call_handler, patch_broker_calls
from propan.rabbit.broker import RabbitBroker
from propan.rabbit.helpers import AioPikaParser
from propan.rabbit.shared.constants import ExchangeType
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
from propan.rabbit.shared.wrapper import AMQPHandlerCallWrapper
from propan.rabbit.types import AioPikaSendableMessage
from propan.types import AnyCallable

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
    message: AioPikaSendableMessage = "",
    queue: Union[RabbitQueue, str] = "",
    exchange: Union[RabbitExchange, str, None] = None,
    *,
    routing_key: str = "",
    **message_kwargs: AnyDict,
) -> PatchedMessage:
    que, exch = RabbitQueue.validate(queue), RabbitExchange.validate(exchange)
    msg = AioPikaParser.encode_message(message, **message_kwargs)

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
    message: AioPikaSendableMessage = "",
    queue: Union[RabbitQueue, str] = "",
    exchange: Union[RabbitExchange, str, None] = None,
    *,
    routing_key: str = "",
    mandatory: bool = True,
    immediate: bool = False,
    timeout: TimeoutType = None,
    rpc: bool = False,
    rpc_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
    **message_kwargs: AnyDict,
) -> Any:
    exch = RabbitExchange.validate(exchange)

    incoming = build_message(
        message=message,
        queue=queue,
        exchange=exch,
        routing_key=routing_key,
        **message_kwargs,
    )

    for handler in self.handlers.values():  # pragma: no branch
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

            elif handler.exchange.type == ExchangeType.HEADERS:  # pramga: no branch
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

            else:  # pragma: no cover
                assert_never(handler.exchange.type)

            if call:
                r = await call_handler(
                    handler=handler,
                    message=incoming,
                    rpc=rpc,
                    rpc_timeout=rpc_timeout,
                    raise_timeout=raise_timeout,
                )
                if rpc:  # pragma: no branch
                    return r


class TestableRabbitBroker(RabbitBroker):
    subscriber_mocks: Dict[AnyCallable, MagicMock]


def patch_publishers(broker: RabbitBroker, wrapper: AMQPHandlerCallWrapper) -> None:
    for publisher in wrapper._publishers:

        @broker.subscriber(
            queue=publisher.queue,
            exchange=publisher.exchange,
            _raw=True,
        )
        def f(msg):
            pass

        exc_name = publisher.exchange.name if publisher.exchange else "default"
        exc_responses = wrapper.response_mocks.get(exc_name, {})
        exc_responses[publisher.queue.name] = f.mock
        wrapper.response_mocks[exc_name] = exc_responses


def TestRabbitBroker(broker: RabbitBroker) -> TestableRabbitBroker:
    broker._channel = AsyncMock()
    broker.declarer = AsyncMock()
    patch_broker_calls(broker, patch_publishers)
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock(side_effect=partial(patch_broker_calls, broker, patch_publishers))  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
