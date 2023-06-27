import asyncio
import logging
from functools import wraps
from secrets import token_hex
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import anyio
import nats
from fast_depends.dependencies import Depends
from nats.aio.client import Callback, Client, ErrorCallback
from nats.aio.msg import Msg
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import AnyDict, DecodedMessage, DecoratedCallable, SendableMessage
from propan.utils import context

T = TypeVar("T")
NatsMessage: TypeAlias = PropanMessage[Msg]


class NatsBroker(BrokerUsecase[Msg, Client]):
    handlers: List[Handler]

    __max_queue_len: int
    __max_subject_len: int
    __is_connected: bool

    def __init__(
        self,
        servers: Union[str, List[str]] = ["nats://localhost:4222"],  # noqa: B006
        *,
        log_fmt: Optional[str] = None,
        protocol: str = "nats",
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            servers, log_fmt=log_fmt, url_=servers, protocol=protocol, **kwargs
        )

        self._connection = None

        self.__max_queue_len = 0
        self.__max_subject_len = 4
        self.__is_connected = True

    async def _connect(
        self,
        *,
        url: Optional[str] = None,
        error_cb: Optional[ErrorCallback] = None,
        reconnected_cb: Optional[Callback] = None,
        **kwargs: Any,
    ) -> Client:
        if url is not None:
            kwargs["servers"] = kwargs.pop("servers", []) + [url]
        return await nats.connect(
            error_cb=self.log_connection_broken(error_cb),
            reconnected_cb=self.log_reconnected(reconnected_cb),
            **kwargs,
        )

    def handle(
        self,
        subject: str,
        queue: str = "",
        *,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[[DecoratedCallable], None]:
        super().handle()

        self.__max_subject_len = max((self.__max_subject_len, len(subject)))
        self.__max_queue_len = max((self.__max_queue_len, len(queue)))

        def wrapper(func: DecoratedCallable) -> None:
            func, dependant = self._wrap_handler(
                func,
                queue=queue,
                subject=subject,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                subject=subject,
                queue=queue,
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

        for handler in self.handlers:
            func = handler.callback

            c = self._get_log_context(None, handler.subject, handler.queue)
            self._log(f"`{func.__name__}` waiting for messages", extra=c)

            sub = await self._connection.subscribe(
                subject=handler.subject,
                queue=handler.queue,
                cb=func,
            )
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
    ) -> Optional[DecodedMessage]:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        msg, content_type = self._encode_message(message)

        client = self._connection

        if callback is True:
            if reply_to:
                raise ValueError(
                    "You should use `reply_to` to send response to long-living queue "
                    "and `callback` to get response in sync mode."
                )

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
            if raise_timeout:
                scope = anyio.fail_after
            else:
                scope = anyio.move_on_after

            msg: Any = None
            with scope(callback_timeout):
                msg = await future

            if msg:
                if msg.headers:  # pragma: no branch
                    if (
                        msg.headers.get(nats.js.api.Header.STATUS)
                        == nats.aio.client.NO_RESPONDERS_STATUS
                    ):
                        raise nats.errors.NoRespondersError
                return await self._decode_message(await self._parse_message(msg))

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)
        for h in self.handlers:
            if h.subscription is not None:
                await h.subscription.unsubscribe()
                h.subscription = None

        if self._connection is not None:
            await self._connection.drain()
            self._connection = None

    def _get_log_context(
        self,
        message: Optional[NatsMessage],
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

    async def _parse_message(self, message: Msg) -> NatsMessage:
        return PropanMessage(
            body=message.data,
            content_type=message.header.get("content-type", ""),
            headers=message.header,
            reply_to=message.reply,
            raw_message=message,
        )

    def _process_message(
        self,
        func: Callable[[NatsMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher] = None,
    ) -> Callable[[NatsMessage], Awaitable[T]]:
        @wraps(func)
        async def wrapper(message: NatsMessage) -> T:
            r = await func(message)

            if message.reply_to:
                await self.publish(r, message.reply_to)

            return r

        return wrapper

    def log_connection_broken(
        self, error_cb: Optional[ErrorCallback] = None
    ) -> ErrorCallback:
        c = self._get_log_context(None, "")

        async def wrapper(err: Exception) -> None:
            if error_cb is not None:
                await error_cb(err)

            if self.__is_connected is True:
                self._log(err, logging.WARNING, c)
                self.__is_connected = False

        return wrapper

    def log_reconnected(self, cb: Optional[Callback] = None) -> Callback:
        c = self._get_log_context(None, "")

        async def wrapper() -> None:
            if cb is not None:
                await cb()

            if self.__is_connected is False:
                self._log("Connection established", logging.INFO, c)
                self.__is_connected = True

        return wrapper
