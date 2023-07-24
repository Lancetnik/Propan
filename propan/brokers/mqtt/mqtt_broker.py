from typing import Any, Callable, Optional, TypeVar, Type, List
from types import TracebackType
from functools import wraps

from paho.mqtt.client import Client
from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.mqtt.schemas import Handler
from propan.types import SendableMessage, AnyDict

T = TypeVar("T")


class MqttBroker(BrokerAsyncUsecase[Any, Client]):
    handlers: List[Handler]

    _connection: Client
    _polling_interval: float

    def __init__(
        self,
        url: str = "localhost",
        *,
        polling_interval: float = 1.0,
        log_fmt: Optional[str] = None,
        protocol: str = "mqtt",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(url, log_fmt=log_fmt, url_=url, protocol=protocol, **kwargs)
        self._polling_interval = polling_interval

    async def _connect(self, url: str, **kwargs: AnyDict) -> Client:
        client = Client()
        client.connect(url, **kwargs)
        return client

    async def close(  # type: ignore[override]
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)
        if self._connection is not None:
            self._connection.disconnect()
            self._connection = None

    async def start(self) -> None:
        await super().start()

        for h in self.handlers:
            self._connection.subscribe(h.topic)
            self._connection.message_callback_add(h.topic, h.callback)

        self._connection.loop_start()

    def handle(self, topic: str):
        def wrapper(
            func: Callable[[PropanMessage], Any]
        ) -> Callable[[PropanMessage], Any]:
            func = wrap_mqtt(func)
            # func, dependant = self._wrap_handler(func)
            handler = Handler(
                callback=func,
                # dependant=dependant,
                topic=topic,
            )
            self.handlers.append(handler)
            return func

        return wrapper

    async def _parse_message(self, message) -> PropanMessage:
        client, userdata, msg = message
        return PropanMessage(
            body=msg.body,
            raw_message=message,
        )

    async def _process_message(
        self,
        func,
        watcher,
    ):
        @wraps(func)
        async def wrapper(message: PropanMessage[Any]) -> T:
            r = await func(message)
            return r
        return wrapper

    async def publish(
        self,
        message: SendableMessage,
        *args: Any,
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
        **kwargs: Any,
    ) -> Any:
        self._connection.publish()


def wrap_mqtt(func):
    @wraps(func)
    def wrap(client, userdata, msg):
        return (client, userdata, msg)
    return wrap
