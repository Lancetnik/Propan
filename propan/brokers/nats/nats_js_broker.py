# TODO: remove mypy ignore at complete
# type: ignore
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar

import nats
from nats.js.client import JetStreamContext

from propan._compat import model_to_dict
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.nats.nats_broker import NatsBroker
from propan.brokers.nats.schemas import JetStream
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext
from propan.types import AnyDict

T = TypeVar("T")


class NatsJSBroker(NatsBroker):
    _js: Optional[JetStream] = None
    _connection: Optional[JetStreamContext] = None

    def __init__(self, *args: Any, jetstream: JetStream, **kwargs: AnyDict):
        super().__init__(*args, **kwargs)
        self._js = jetstream

    async def _connect(self, *args: Any, **kwargs: AnyDict) -> JetStreamContext:
        assert self._js

        nc = await nats.connect(*args, **kwargs)

        stream = await nc.jetstream(
            **model_to_dict(self._js, include={"prefix", "domain", "timeout"})
        )

        return stream

    @staticmethod
    def _process_message(
        func: Callable[[PropanMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher] = None,
    ) -> Callable[[PropanMessage], Awaitable[T]]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            if watcher is None:
                return await func(message)
            else:
                async with WatcherContext(
                    watcher,
                    message.message_id,
                    on_success=message.raw_message.ack,
                    on_error=message.raw_message.nak,
                    on_max=message.raw_message.term,
                ):
                    await message.in_progress()
                    return await func(message)

        return wrapper
