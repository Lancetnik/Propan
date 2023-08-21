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
from nats.aio.subscription import (
    DEFAULT_SUB_PENDING_BYTES_LIMIT,
    DEFAULT_SUB_PENDING_MSGS_LIMIT,
)
from typing_extensions import TypeAlias

from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import WRONG_PUBLISH_ARGS
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context

T = TypeVar("T")
NatsMessage: TypeAlias = PropanMessage[Msg]


class NatsBroker(BrokerAsyncUsecase[Msg, Client]):
    handlers: List[Handler]

    _max_queue_len: int
    _max_subject_len: int
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

        self._max_queue_len = 0
        self._max_subject_len = 4
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
        pending_msgs_limit: int = DEFAULT_SUB_PENDING_MSGS_LIMIT,
        pending_bytes_limit: int = DEFAULT_SUB_PENDING_BYTES_LIMIT,
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Msg, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle()

        self._max_subject_len = max((self._max_subject_len, len(subject)))
        self._max_queue_len = max((self._max_queue_len, len(queue)))

        def wrapper(
            func: HandlerCallable[T_HandlerReturn],
        ) -> Callable[[Msg, bool], Awaitable[T_HandlerReturn]]:
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
                extra_args={
                    "pending_msgs_limit": pending_msgs_limit,
                    "pending_bytes_limit": pending_bytes_limit,
                },
            )
            self.handlers.append(handler)

            return func

        return wrapper

    async def start(self) -> None:
        context.set_local(
            "log_context",
            self._get_log_context(None, ""),
        )

        await self._start()

        for handler in self.handlers:
            func = handler.callback

            c = self._get_log_context(None, handler.subject, handler.queue)
            self._log(f"`{func.__name__}` waiting for messages", extra=c)

            sub = await self._connection.subscribe(
                subject=handler.subject,
                queue=handler.queue,
                cb=func,
                **handler.extra_args,
            )
            handler.subscription = sub

    async def _start(self):
        await super().start()

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
                raise WRONG_PUBLISH_ARGS

            token = client._nuid.next()
            token.extend(token_hex(2).encode())
            reply_to = token.decode()

        if reply_to:
            future: asyncio.Future[Msg] = asyncio.Future()
            sub = await client.subscribe(reply_to, future=future, max_msgs=1)
            await sub.unsubscribe(limit=1)

            kwargs = {"reply": reply_to}

        else:
            kwargs = {}

        await client.publish(
            subject=subject,
            payload=msg,
            headers={
                **(headers or {}),
                "content-type": content_type or "",
            },
            **kwargs,
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
            f"%(subject)-{self._max_subject_len}s | "
            + (f"%(queue)-{self._max_queue_len}s | " if self._max_queue_len else "")
            + "%(message_id)-10s "
            "- %(message)s"
        )

    async def _parse_message(self, message: Msg) -> NatsMessage:
        headers = message.header or {}
        return PropanMessage(
            body=message.data,
            content_type=headers.get("content-type", ""),
            headers=headers,
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
                self._log(err, logging.WARNING, c, exc_info=err)
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
