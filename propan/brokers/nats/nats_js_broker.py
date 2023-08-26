import asyncio
import logging
from contextlib import suppress
from functools import wraps
from secrets import token_hex
from types import TracebackType
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar

import anyio
import nats.errors
import nats.js
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js.client import (
    DEFAULT_JS_SUB_PENDING_BYTES_LIMIT,
    DEFAULT_JS_SUB_PENDING_MSGS_LIMIT,
    JetStreamContext,
)

from propan.brokers._model.broker_usecase import HandlerCallable, T_HandlerReturn
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import WRONG_PUBLISH_ARGS
from propan.brokers.nats import consts as api
from propan.brokers.nats.nats_broker import NatsBroker, NatsMessage
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import (
    BaseWatcher,
    NotPushBackWatcher,
    WatcherContext,
)
from propan.types import AnyDict, DecodedMessage, SendableMessage

T = TypeVar("T")


class NatsJSBroker(NatsBroker):
    _raw_connection: Optional[Client]
    _connection: Optional[JetStreamContext]
    _stream_config: api.StreamConfig

    @property
    def js(self) -> JetStreamContext:
        assert self._connection, "You should start connection first"
        return self._connection

    def __init__(
        self,
        *args: Any,
        # JS
        stream: Optional[str] = "propan-stream",
        description: Optional[str] = None,
        retention: Optional[api.RetentionPolicy] = None,
        max_consumers: Optional[int] = None,
        max_msgs: Optional[int] = None,
        max_bytes: Optional[int] = None,
        discard: Optional[api.DiscardPolicy] = api.DiscardPolicy.OLD,
        max_age: Optional[float] = None,  # in seconds
        max_msgs_per_subject: int = -1,
        max_msg_size: Optional[int] = -1,
        storage: Optional[api.StorageType] = None,
        num_replicas: Optional[int] = None,
        no_ack: bool = False,
        template_owner: Optional[str] = None,
        duplicate_window: int = 0,
        placement: Optional[api.Placement] = None,
        mirror: Optional[api.StreamSource] = None,
        sources: Optional[List[api.StreamSource]] = None,
        sealed: bool = False,
        deny_delete: bool = False,
        deny_purge: bool = False,
        allow_rollup_hdrs: bool = False,
        republish: Optional[api.RePublish] = None,
        allow_direct: Optional[bool] = None,
        mirror_direct: Optional[bool] = None,
        # custom
        declare_stream: bool = True,
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._raw_connection = None
        self._declare_stream = declare_stream
        self._stream_config = api.StreamConfig(
            name=stream,
            description=description,
            retention=retention,
            max_consumers=max_consumers,
            max_msgs=max_msgs,
            max_bytes=max_bytes,
            discard=discard,
            max_age=max_age,
            max_msgs_per_subject=max_msgs_per_subject,
            max_msg_size=max_msg_size,
            storage=storage,
            num_replicas=num_replicas,
            no_ack=no_ack,
            template_owner=template_owner,
            duplicate_window=duplicate_window,
            placement=placement,
            mirror=mirror,
            sources=sources,
            sealed=sealed,
            deny_delete=deny_delete,
            deny_purge=deny_purge,
            allow_rollup_hdrs=allow_rollup_hdrs,
            republish=republish,
            allow_direct=allow_direct,
            mirror_direct=mirror_direct,
        )

    async def _connect(
        self,
        *,
        url: Optional[str] = None,
        **kwargs: Any,
    ) -> JetStreamContext:
        nc = await super()._connect(url=url, **kwargs)
        stream = nc.jetstream()
        self._raw_connection = nc
        return stream

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super(NatsBroker, self).close(exc_type, exc_val, exec_tb)
        for h in self.handlers:
            if h.subscription is not None:
                await h.subscription.unsubscribe()
                h.subscription = None

        if self._raw_connection is not None:
            await self._raw_connection.drain()
            self._raw_connection = None

    async def _start(self):
        await super()._start()
        if self._declare_stream:
            subjects = {h.subject for h in self.handlers}
            try:  # pragma: no branch
                await self._connection.add_stream(
                    config=self._stream_config,
                    subjects=tuple(subjects),
                )
            except nats.js.errors.BadRequestError as e:
                old_config = (
                    await self._connection.stream_info(self._stream_config.name)
                ).config

                c = self._get_log_context(None, "")
                if (
                    e.description
                    == "stream name already in use with a different configuration"
                ):
                    self._log(e, logging.WARNING, c)
                    await self._connection.update_stream(
                        config=self._stream_config,
                        subjects=tuple(set(old_config.subjects).union(subjects)),
                    )
                else:  # pragma: no cover
                    self._log(e, logging.ERROR, c, exc_info=e)

    def _process_message(
        self,
        func: Callable[[NatsMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher] = None,
    ) -> Callable[[NatsMessage], Awaitable[T]]:
        if watcher is None:  # pragma: no branch
            watcher = NotPushBackWatcher()

        @wraps(func)
        async def wrapper(message: NatsMessage) -> T:
            context = WatcherContext(
                watcher,
                message,
                on_success=message_ack,
                on_error=message_nak,
                on_max=message_term,
            )

            async with context:
                await message.raw_message.in_progress()

                r = await func(message)

                if message.reply_to:
                    reply_msg, content_type = self._encode_message(r)

                    await self._raw_connection.publish(
                        subject=message.reply_to,
                        payload=reply_msg,
                        headers={
                            "content-type": content_type or "",
                        },
                    )

            return r

        return wrapper

    async def _parse_message(self, message: Msg) -> NatsMessage:
        headers = message.header or {}
        return PropanMessage(
            body=message.data,
            content_type=headers.get("content-type", ""),
            headers=headers,
            reply_to=headers.get("reply_to", ""),
            raw_message=message,
        )

    def handle(
        self,
        subject: str,
        queue: str = "",
        *,
        durable: Optional[str] = None,
        config: Optional[api.ConsumerConfig] = None,
        ordered_consumer: bool = False,
        idle_heartbeat: Optional[float] = None,
        flow_control: bool = False,
        pending_msgs_limit: Optional[int] = DEFAULT_JS_SUB_PENDING_MSGS_LIMIT,
        pending_bytes_limit: Optional[int] = DEFAULT_JS_SUB_PENDING_BYTES_LIMIT,
        deliver_policy: Optional[api.DeliverPolicy] = None,
        headers_only: Optional[bool] = None,
        # broker kwargs
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Msg, bool], Awaitable[T_HandlerReturn]],
    ]:
        super(NatsBroker, self).handle()
        self._max_subject_len = max((self._max_subject_len, len(subject)))
        self._max_queue_len = max((self._max_queue_len, len(queue)))

        def wrapper(func: HandlerCallable) -> HandlerCallable:
            func, dependant = self._wrap_handler(
                func,
                queue=queue,
                subject=subject,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                subject=subject,
                queue=queue,
                _description=description,
                dependant=dependant,
                extra_args={
                    "stream": self._stream_config.name,
                    "durable": durable,
                    "manual_ack": True,
                    "ordered_consumer": ordered_consumer,
                    "idle_heartbeat": idle_heartbeat,
                    "flow_control": flow_control,
                    "config": config,
                    "pending_msgs_limit": pending_msgs_limit,
                    "pending_bytes_limit": pending_bytes_limit,
                    "deliver_policy": deliver_policy,
                    "headers_only": headers_only,
                },
            )
            self.handlers.append(handler)

            return func

        return wrapper

    async def publish(
        self,
        message: SendableMessage,
        subject: str,
        *,
        stream: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> Optional[DecodedMessage]:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        payload, content_type = self._encode_message(message)

        client = self._raw_connection

        if callback is True:
            if reply_to:
                raise WRONG_PUBLISH_ARGS

            token = client._nuid.next()
            token.extend(token_hex(2).encode())
            reply_to = token.decode()
            future: asyncio.Future[Msg] = asyncio.Future()
            sub = await client.subscribe(reply_to, future=future, max_msgs=1)
            await sub.unsubscribe(limit=1)

        if raise_timeout:
            scope = anyio.fail_after
        else:
            scope = anyio.move_on_after

        with suppress(nats.errors.TimeoutError):  # py37 compatibility
            with scope(callback_timeout):
                await self._connection.publish(
                    subject=subject,
                    payload=payload,
                    headers={
                        **(headers or {}),
                        "reply_to": reply_to,
                        "content-type": content_type or "",
                    },
                    timeout=callback_timeout,
                    stream=stream or self._stream_config.name,
                )

        if callback:
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


async def message_ack(message: NatsMessage) -> None:
    with suppress(nats.errors.MsgAlreadyAckdError):
        await message.raw_message.ack()


async def message_nak(message: NatsMessage) -> None:
    with suppress(nats.errors.MsgAlreadyAckdError):
        await message.raw_message.nak()


async def message_term(message: NatsMessage) -> None:
    with suppress(nats.errors.MsgAlreadyAckdError):
        await message.raw_message.term()
