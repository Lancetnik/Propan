import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, List, NoReturn, Optional, TypeVar
from uuid import uuid4

from redis.asyncio.client import PubSub, Redis
from redis.asyncio.connection import ConnectionPool, parse_url

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage, RawDecoced
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.redis.schemas import Handler, RedisMessage
from propan.types import (
    AnyCallable,
    DecodedMessage,
    DecoratedCallable,
    HandlerWrapper,
    SendableMessage,
)

T = TypeVar("T")


class RedisBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Redis
    __max_channel_len: int
    _polling_interval: float

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        polling_interval: float = 1.0,
        *,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(url=url, log_fmt=log_fmt, **kwargs)
        self.__max_channel_len = 0
        self._polling_interval = polling_interval

    async def _connect(
        self,
        url: str,
        **kwargs: Any,
    ) -> Redis:
        url_options = parse_url(url)
        url_options.update(kwargs)
        pool = ConnectionPool(**url_options)
        return Redis(connection_pool=pool)

    async def connect(
        self,
        url: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Coroutine[Any, Any, Any]:
        if url is not None:
            kwargs["url"] = url
        return await super().connect(*args, **kwargs)

    async def close(self) -> None:
        for h in self.handlers:
            if h.task is not None:  # pragma: no branch
                h.task.cancel()
                h.task = None

            if h.subscription is not None:  # pragma: no branch
                await h.subscription.unsubscribe()
                await h.subscription.reset()
                h.subscription = None

        if self._connection is not None:  # pragma: no branch
            await self._connection.close()
            self._connection = None

    def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            r = await func(message)

            msg = message.raw_message
            if isinstance(msg, RedisMessage) and message.reply_to:
                await self.publish(r or "", message.reply_to)

            return r

        return wrapper

    def handle(
        self,
        channel: str = "",
        *,
        pattern: bool = False,
    ) -> HandlerWrapper:
        self.__max_channel_len = max(self.__max_channel_len, len(channel))

        def wrapper(func: AnyCallable) -> DecoratedCallable:
            func = self._wrap_handler(
                func,
                channel=channel,
            )
            handler = Handler(callback=func, channel=channel, pattern=pattern)
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        await super().start()

        for handler in self.handlers:  # pragma: no branch
            c = self._get_log_context(None, handler.channel)
            self._log(f"`{handler.callback.__name__}` waiting for messages", extra=c)

            psub = self._connection.pubsub()
            if handler.pattern is True:
                await psub.psubscribe(handler.channel)
            else:
                await psub.subscribe(handler.channel)

            handler.subscription = psub
            handler.task = asyncio.create_task(self._consume(handler, psub))

    async def publish(
        self,
        message: SendableMessage = "",
        channel: str = "",
        *,
        reply_to: str = "",
        headers: Optional[Dict[str, Any]] = None,
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> None:
        if self._connection is None:
            raise ValueError("Redis connection not established yet")

        msg, content_type = self._encode_message(message)

        if callback is True:
            callback_channel = str(uuid4())
            psub = self._connection.pubsub()
            response_queue = asyncio.Queue(maxsize=1)
            await psub.subscribe(callback_channel)
            task = asyncio.create_task(_consume_one(response_queue, psub))
        else:
            callback_channel = reply_to
            psub = None
            response_queue = None
            task = None

        await self._connection.publish(
            channel,
            RedisMessage(
                data=msg,
                headers={
                    "content-type": content_type or "",
                    **(headers or {}),
                },
                reply_to=callback_channel,
            ).json(),
        )

        if psub and response_queue and task:
            try:
                response = await asyncio.wait_for(
                    response_queue.get(), callback_timeout
                )
            except asyncio.TimeoutError as e:
                if raise_timeout is True:
                    raise e
                return None
            else:
                return await self._decode_message(await self._parse_message(response))
            finally:
                await psub.unsubscribe(callback_channel)
                await psub.reset()
                task.cancel()

    @staticmethod
    async def _parse_message(message: Any) -> PropanMessage:
        data = message.get("data", b"")

        try:
            obj = RedisMessage.parse_raw(data)
        except Exception:
            msg = PropanMessage(
                body=data,
                raw_message=message,
            )
        else:
            msg = PropanMessage(
                body=obj.data,
                content_type=obj.headers.get("content-type", ""),
                reply_to=obj.reply_to,
                headers=obj.headers,
                raw_message=obj,
            )

        return msg

    async def _decode_message(self, message: PropanMessage) -> DecodedMessage:
        if message.headers.get("content-type") is not None:
            return await super()._decode_message(message)
        else:
            return RawDecoced(message=message.body).message

    def _get_log_context(
        self, message: Optional[PropanMessage], channel: str
    ) -> Dict[str, Any]:
        context = {
            "channel": channel,
            **super()._get_log_context(message),
        }
        return context

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(channel)-{self.__max_channel_len}s | "
            "%(message_id)-10s "
            "- %(message)s"
        )

    async def _consume(self, handler: Handler, psub: PubSub) -> NoReturn:
        c = self._get_log_context(None, handler.channel)

        connected = True
        while True:
            try:
                m = await psub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=self._polling_interval,
                )
            except Exception:
                if connected is True:
                    self._log("Connection broken", logging.WARNING, c)
                    connected = False
                await asyncio.sleep(5)
            else:
                if connected is False:
                    self._log("Connection established", logging.INFO, c)
                    connected = True

                if m:  # pragma: no branch
                    await handler.callback(m)
            finally:
                await asyncio.sleep(0.01)


async def _consume_one(queue: asyncio.Queue, psub: PubSub) -> NoReturn:
    async for m in psub.listen():
        t = m.get("type")
        if t and "message" in t:  # pragma: no branch
            await queue.put(m)
            break
