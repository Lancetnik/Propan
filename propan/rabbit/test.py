import re
import sys
from functools import partial
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
from typing_extensions import assert_never

from propan.broker.test import call_handler, patch_broker_calls
from propan.rabbit.broker import RabbitBroker
from propan.rabbit.helpers import AioPikaParser
from propan.rabbit.shared.constants import ExchangeType
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
from propan.rabbit.types import AioPikaSendableMessage

__all__ = ("TestRabbitBroker",)


def TestRabbitBroker(broker: RabbitBroker) -> RabbitBroker:
    broker._channel = AsyncMock()
    broker.declarer = AsyncMock()
    _fake_start(broker)
    broker.start = AsyncMock(wraps=partial(_fake_start, broker))
    broker._connect = MethodType(_fake_connect, broker)
    return broker


class PatchedMessage(IncomingMessage):
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
    reply_to: Optional[str] = None,
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
                    reply_to=reply_to,
                )
            ),
            body=msg.body,
            channel=AsyncMock(),
        )
    )


class FakePublisher:
    def __init__(self, broker: RabbitBroker):
        self.broker = broker

    async def _publish(
        self,
        message: AioPikaSendableMessage = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Any:
        return await self.publish(
            message=message,
            exchange=exchange,
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
            persist=persist,
            reply_to=reply_to,
            **message_kwargs,
        )

    async def publish(
        self,
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
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Any:
        exch = RabbitExchange.validate(exchange)

        incoming = build_message(
            message=message,
            queue=queue,
            exchange=exch,
            routing_key=routing_key,
            reply_to=reply_to,
            **message_kwargs,
        )

        for handler in self.broker.handlers.values():  # pragma: no branch
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


async def _fake_connect(self: RabbitBroker, *args: Any, **kwargs: AnyDict) -> None:
    self._publisher = FakePublisher(self)


def _fake_start(self: RabbitBroker, *args: Any, **kwargs: AnyDict) -> None:
    for p in self._publishers:
        p._publisher = self._publisher

    for publisher in self._publishers:

        @self.subscriber(
            queue=publisher.queue,
            exchange=publisher.exchange,
            _raw=True,
        )
        def f(msg):
            pass

        publisher.mock = f.mock

    patch_broker_calls(self)
