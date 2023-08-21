import asyncio
import logging
from functools import wraps
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    Type,
    TypeVar,
)
from uuid import uuid4

import anyio
from anyio.streams.memory import MemoryObjectSendStream
from fast_depends.dependencies import Depends
from redis.asyncio.client import PubSub, Redis
from redis.asyncio.connection import ConnectionPool, parse_url
from typing_extensions import TypeAlias

from propan._compat import model_parse, model_to_json
from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage, RawDecoced
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.redis.schemas import Handler
from propan.brokers.redis.schemas import RedisMessage as RM
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context

T = TypeVar("T")
RedisMessage: TypeAlias = PropanMessage[AnyDict]


class RedisBroker(BrokerAsyncUsecase):
    handlers: List[Handler]
    _connection: Redis
    __max_channel_len: int
    _polling_interval: float

    def __init__(
        self,
        url: str = "redis://localhost:6379",
        *,
        polling_interval: float = 1.0,
        log_fmt: Optional[str] = None,
        protocol: str = "redis",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            url,
            log_fmt=log_fmt,
            url_=url,
            protocol=protocol,
            **kwargs,
        )
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

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)
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
        func: Callable[[RedisMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[RedisMessage], Awaitable[T]]:
        @wraps(func)
        async def wrapper(message: RedisMessage) -> T:
            r = await func(message)

            msg = message.raw_message
            if isinstance(msg, RM) and message.reply_to:
                await self.publish(r or "", message.reply_to)

            return r

        return wrapper

    def handle(
        self,
        channel: str = "",
        *,
        pattern: bool = False,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle()

        self.__max_channel_len = max(self.__max_channel_len, len(channel))

        def wrapper(
            func: HandlerCallable[T_HandlerReturn],
        ) -> Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]]:
            func, dependant = self._wrap_handler(
                func,
                channel=channel,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                channel=channel,
                pattern=pattern,
                _description=description,
                dependant=dependant,
            )
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, ""),
        )

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
    ) -> Optional[DecodedMessage]:
        if self._connection is None:
            raise ValueError("Redis connection not established yet")

        msg, content_type = self._encode_message(message)

        if callback is True:
            if reply_to:
                raise ValueError(
                    "You should use `reply_to` to send response to long-living queue "
                    "and `callback` to get response in sync mode."
                )

            callback_channel = str(uuid4())
            psub = self._connection.pubsub()
            (
                send_response_stream,
                receive_response_stream,
            ) = anyio.create_memory_object_stream(max_buffer_size=1)
            await psub.subscribe(callback_channel)
            task = asyncio.create_task(_consume_one(send_response_stream, psub))
        else:
            callback_channel = reply_to
            psub = None
            send_response_stream = receive_response_stream = None
            task = None

        await self._connection.publish(
            channel,
            model_to_json(
                RM(
                    data=msg,
                    headers={
                        "content-type": content_type or "",
                        **(headers or {}),
                    },
                    reply_to=callback_channel,
                )
            ),
        )

        if psub and receive_response_stream and task:
            try:
                with anyio.fail_after(callback_timeout):
                    response = await receive_response_stream.receive()
            except TimeoutError as e:
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
    async def _parse_message(message: Any) -> RedisMessage:
        data = message.get("data", b"")

        try:
            obj = model_parse(RM, data)
        except Exception:
            msg = RedisMessage(
                body=data,
                raw_message=message,
            )
        else:
            msg = RedisMessage(
                body=obj.data,
                content_type=obj.headers.get("content-type", ""),
                reply_to=obj.reply_to,
                headers=obj.headers,
                raw_message=obj,
            )

        return msg

    async def _decode_message(self, message: RedisMessage) -> DecodedMessage:
        if message.headers.get("content-type") is not None:
            return await super()._decode_message(message)
        else:
            return RawDecoced(message=message.body).message

    def _get_log_context(
        self, message: Optional[RedisMessage], channel: str
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
            except Exception as e:
                if connected is True:
                    self._log("Connection broken", logging.WARNING, c, exc_info=e)
                    connected = False
                await anyio.sleep(5)
            else:
                if connected is False:
                    self._log("Connection established", logging.INFO, c)
                    connected = True

                if m:  # pragma: no branch
                    await handler.callback(m)
            finally:
                await anyio.sleep(0.01)


async def _consume_one(queue: MemoryObjectSendStream[any], psub: PubSub) -> NoReturn:
    async for m in psub.listen():
        t = m.get("type")
        if t and "message" in t:  # pragma: no branch
            await queue.send(m)
            break
