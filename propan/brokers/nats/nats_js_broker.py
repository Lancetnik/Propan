from functools import partial, wraps
from typing import Callable, Optional

import nats
from nats.aio.msg import Msg
from nats.js.client import JetStreamContext
from propan.brokers.nats.nats_broker import NatsBroker
from propan.brokers.nats.schemas import JetStream
from propan.brokers.push_back_watcher import BaseWatcher, WatcherContext


class NatsJSBroker(NatsBroker):
    _js: Optional[JetStream] = None
    _connection: Optional[JetStreamContext] = None

    def __init__(self, *args, jetstream: JetStream, **kwargs):
        super().__init__(*args, **kwargs)
        self._js = jetstream

    async def _connect(self, *args, **kwargs) -> JetStreamContext:
        nc = await nats.connect(*args, **kwargs)

        stream = await nc.jetstream(
            **self._js.dict(include={"prefix", "domain", "timeout"})
        )

        return stream

    @staticmethod
    def _process_message(
        func: Callable, watcher: Optional[BaseWatcher] = None
    ) -> Callable:
        @wraps(func)
        async def wrapper(message: Msg):
            if watcher is None:
                return await func(message)
            else:
                async with WatcherContext(
                    watcher,
                    message.message_id,
                    on_success=partial(message.ack),
                    on_error=partial(message.nak),
                    on_max=partial(message.term),
                ):
                    await message.in_progress()
                    return await func(message)

        return wrapper
