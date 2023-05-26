import asyncio
from functools import wraps
from secrets import token_hex
from typing import Any, Callable, Dict, List, Optional, TypeVar

import nats
from nats.aio.client import Client
from nats.aio.msg import Msg

from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import AnyDict, DecoratedCallable, SendableMessage

T = TypeVar("T")


class NatsBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[Client]

    __max_queue_len: int
    __max_subject_len: int

    def __init__(self, *args: Any, log_fmt: Optional[str] = None, **kwargs: AnyDict):
        super().__init__(*args, log_fmt=log_fmt, **kwargs)

        self._connection = None

        self.__max_queue_len = 0
        self.__max_subject_len = 4

    async def _connect(
        self,
        *args: Any,
        url: Optional[str] = None,
        **kwargs: Any,
    ) -> Client:
        if url is not None:
            kwargs["servers"] = kwargs.pop("servers", []) + [url]
        return await nats.connect(*args, **kwargs)

    def handle(
        self,
        subject: str,
        queue: str = "",
        **original_kwargs,
    ) -> Callable[[DecoratedCallable], None]:
        self.__max_subject_len = max((self.__max_subject_len, len(subject)))
        self.__max_queue_len = max((self.__max_queue_len, len(queue)))

        def wrapper(func: DecoratedCallable) -> None:
            func = self._wrap_handler(
                func, queue=queue, subject=subject, **original_kwargs
            )
            handler = Handler(callback=func, subject=subject, queue=queue)
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        await super().start()

        for handler in self.handlers:
            func = handler.callback

            c = self._get_log_context(None, handler.subject, handler.queue)
            self._log(f"`{func.__name__}` waiting for messages", extra=c)

            sub = await self._connection.subscribe(handler.subject, cb=func)
            handler.subscription = sub

    async def publish(
        self,
        message: SendableMessage,
        subject: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> None:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        msg, content_type = self._encode_message(message)

        client = self._connection

        if callback is True and not reply_to:
            token = client._nuid.next()
            token.extend(token_hex(2).encode())
            reply_to = token.decode()

        if reply_to:
            future: asyncio.Future[Msg] = asyncio.Future()
            sub = await client.subscribe(reply_to, future=future, max_msgs=1)
            await sub.unsubscribe(limit=1)

        await self._connection.publish(
            subject=subject,
            payload=msg,
            reply=reply_to,
            headers={
                **(headers or {}),
                "content-type": content_type or "",
            },
        )

        if reply_to:
            try:
                msg = await asyncio.wait_for(future, callback_timeout)
                if msg.headers:  # pragma: no branch
                    if (
                        msg.headers.get(nats.js.api.Header.STATUS)
                        == nats.aio.client.NO_RESPONDERS_STATUS
                    ):
                        raise nats.errors.NoRespondersError
            except asyncio.TimeoutError as e:
                await sub.unsubscribe()
                future.cancel()
                if raise_timeout is True:
                    raise e
                return None
            else:
                return await self._decode_message(await self._parse_message(msg))

    async def close(self) -> None:
        for h in self.handlers:
            if h.subscription is not None:
                await h.subscription.unsubscribe()
                h.subscription = None

        if self._connection is not None:
            await self._connection.drain()
            self._connection = None

    def _get_log_context(
        self,
        message: Optional[PropanMessage],
        subject: str,
        queue: str = "",
    ) -> Dict[str, Any]:
        context = {
            "subject": subject,
            "queue": queue,
            **super()._get_log_context(message),
        }
        return context

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(subject)-{self.__max_subject_len}s | "
            + (f"%(queue)-{self.__max_queue_len}s | " if self.__max_queue_len else "")
            + "%(message_id)-10s "
            "- %(message)s"
        )

    async def _parse_message(self, message: Msg) -> PropanMessage:
        return PropanMessage(
            body=message.data,
            content_type=message.header.get("content-type", ""),
            headers=message.header,
            reply_to=message.reply,
            raw_message=message,
        )

    def _process_message(
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher] = None
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            r = await func(message)

            if message.reply_to:
                await self.publish(r, message.reply_to)

            return r

        return wrapper
