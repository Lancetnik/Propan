from typing import Any, Callable, Optional, TypeVar

from paho.mqtt.client import Client
from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import HandlerWrapper, SendableMessage

T = TypeVar("T")


class MqttBroker(BrokerAsyncUsecase):
    handlers: list
    _connection: Client
    _polling_interval: float

    def __init__(
        self,
        url: str = "mqtt.eclipseprojects.io",
        *,
        polling_interval: float = 1.0,
        log_fmt: Optional[str] = None,
        protocol: str = "mqtt",
        **kwargs: Any,
    ) -> None:
        super().__init__(url, log_fmt=log_fmt, url_=url, protocol=protocol, **kwargs)
        self._polling_interval = polling_interval

    async def _connect(self, url: str, **kwargs: Any) -> Client:
        client = Client()
        client.connect(url, 1883, 60)
        return client

    async def close(
        self,
    ) -> None:
        await super().close()
        self.client.disconnect()
        self.client = None

    def handle(self, topic: str) -> HandlerWrapper:
        def wrapper(
            func: Callable[[PropanMessage], Any]
        ) -> Callable[[PropanMessage], Any]:
            self.client.subscribe(topic)
            self.client.message_callback_add(topic, func)
            return func

        return wrapper


    async def start(self) -> None:
        self.client.loop_start()

    async def _parse_message(self, message: Any) -> PropanMessage:
        pass

    async def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]:
        pass

    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: Any,
    ) -> Any:
        pass
