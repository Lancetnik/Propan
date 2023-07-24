import sys
from types import MethodType
from typing import Any, Dict, Optional, Union

from typing_extensions import TypeAlias

if sys.version_info < (3, 8):
    from asyncmock import AsyncMock
else:
    from unittest.mock import AsyncMock

from paho.mqtt.client import MQTTMessage

from propan._compat import model_to_json
from propan.brokers.mqtt.mqtt_broker import MqttBroker
from propan.brokers.mqtt.schemas import Handler
from propan.test.utils import call_handler
from propan.types import SendableMessage

__all__ = (
    "build_message",
    "TestMqttBroker",
)

Msg: TypeAlias = Dict[str, Union[bytes, str, None]]


def build_message(
    message: SendableMessage,
    topic: str,
    *,
    headers: Optional[Dict[str, Any]] = None,
) -> Msg:
    msg = MQTTMessage()
    msg.topic = topic
    msg.payload = message
    return msg


async def publish(
    self: MqttBroker,
    message: SendableMessage,
    topic: str,
    *,
    reply_to: str = "",
    headers: Optional[Dict[str, Any]] = None,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    incoming = build_message(
        message=message,
        topic=topic,
        headers=headers,
    )

    for handler in self.handlers:  # pragma: no branch
        if handler.topic == topic:
            r = await call_handler(
                handler, incoming, callback, callback_timeout, raise_timeout
            )
            if callback:  # pragma: no branch
                return r


def TestMqttBroker(broker: MqttBroker) -> MqttBroker:
    broker.connect = AsyncMock()  # type: ignore
    broker.start = AsyncMock()  # type: ignore
    broker.publish = MethodType(publish, broker)  # type: ignore
    return broker
