import asyncio
from dataclasses import dataclass
from typing import Any, List, NoReturn, Optional

from redis.asyncio.client import PubSub, Redis

from propan.brokers.model import BrokerUsecase


@dataclass
class Handler(BaseHandler):
    channel: str
    pattern: bool = False

    task: Optional["asyncio.Task[Any]"] = None
    subscription: Optional[PubSub] = None


class RedisBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Redis

    async def close(self) -> None:
        for h in self.handlers:
            if h.task is not None:
                h.task.cancel()

            if h.subscription is not None:
                await h.subscription.unsubscribe()
                await h.subscription.reset()

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def start(self) -> None:
        await super().start()

        for handler in self.handlers:
            psub = self._connection.pubsub()
            await psub.subscribe(handler.channel)

            handler.subscription = psub
            handler.task = asyncio.create_task(_consume(handler, psub))


async def _consume(handler: Handler, psub: PubSub) -> NoReturn:
    while True:
        m = await psub.get_message(
            ignore_subscribe_messages=True,
            timeout=1.0,
        )
        if m:
            await handler.callback(m)
        await asyncio.sleep(0.01)
