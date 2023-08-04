from contextlib import contextmanager
from types import MethodType
from typing import Any, Optional, Union

from propan.types import AnyDict

from uuid import uuid4

from propan.brokers.rabbit import (
    RabbitSyncBroker,
    RabbitExchange,
    RabbitQueue,
)
from propan.brokers.rabbit.rabbit_broker import PikaSendableMessage, TimeoutType
from propan.brokers.rabbit.utils import validate_exchange, validate_queue
from propan.test.utils import call_handler

__all__ = (
    "build_message",
    "TestRabbitSyncBroker",
)


class PatchedMessage:
    @contextmanager
    def process(self):
        yield

    def ack(self, multiple: bool = False) -> None:
        pass

    def nack(self, multiple: bool = False, requeue: bool = True) -> None:
        pass

    def reject(self, requeue: bool = False) -> None:
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
    msg = RabbitSyncBroker._validate_message(message, None, **message_kwargs)

    routing = routing_key or (que.name if que else "")

    return PatchedMessage(
        # the content of this would need to be adjusted to work synchronously
    )


def publish(
    self: RabbitSyncBroker,
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

    for handler in self.handlers:
        if handler.exchange == exch:
            call = False

            # the logic for determining whether to call would stay the same

            if call:
                r = call_handler(
                    handler,
                    incoming,
                    callback,
                    callback_timeout,
                    raise_timeout,
                )
                if callback:
                    return r


def TestRabbitSyncBroker(broker: RabbitSyncBroker) -> RabbitSyncBroker:
    # the setup of the broker would need to be adjusted to work synchronously
    broker.publish = MethodType(publish, broker)
    return broker
