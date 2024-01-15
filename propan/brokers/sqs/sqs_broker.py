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
    Union,
)
from uuid import uuid4

import anyio
from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from fast_depends.dependencies import Depends
from typing_extensions import TypeAlias

from propan._compat import model_to_dict
from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.exceptions import SkipMessage
from propan.brokers.push_back_watcher import (
    BaseWatcher,
    NotPushBackWatcher,
    WatcherContext,
)
from propan.brokers.sqs.schema import Handler
from propan.brokers.sqs.schema import SQSMessage as SM
from propan.brokers.sqs.schema import SQSQueue
from propan.types import AnyDict, DecodedMessage, SendableMessage
from propan.utils import context

T = TypeVar("T")
QueueUrl: TypeAlias = str
CorrelationId: TypeAlias = str
SQSMessage: TypeAlias = PropanMessage[AnyDict]


class SQSBroker(BrokerAsyncUsecase[AnyDict, AioBaseClient]):
    _connection: AioBaseClient
    _queues: Dict[str, QueueUrl]
    __max_queue_len: int
    response_queue: str
    response_callbacks: Dict[CorrelationId, "asyncio.Future[DecodedMessage]"]
    handlers: List[Handler]

    def __init__(
        self,
        url: str = "http://localhost:9324/",
        *,
        log_fmt: Optional[str] = None,
        response_queue: str = "",
        protocol: str = "sqs",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            url,
            log_fmt=log_fmt,
            url_=url,
            protocol=protocol,
            **kwargs,
        )
        self._queues = {}
        self.__max_queue_len = 4
        self.response_queue = response_queue
        self.response_callbacks = {}

    async def _connect(self, *, url: str, **kwargs: Any) -> AioBaseClient:
        session = get_session()
        client: AioBaseClient = await session._create_client(
            service_name="sqs", endpoint_url=url, **kwargs
        )
        context.set_global("client", client)
        await client.__aenter__()
        return client

    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        await super().close(exc_type, exc_val, exec_tb)
        for f in self.response_callbacks.values():
            f.cancel()
        self.response_callbacks = {}

        for h in self.handlers:
            if h.task is not None:
                h.task.cancel()
                h.task = None

        if self._connection is not None:
            await self._connection.__aexit__(None, None, None)
            self._connection = None

    async def _parse_message(self, message: Dict[str, Any]) -> SQSMessage:
        attributes = message.get("MessageAttributes", {})

        headers = {i: j.get("StringValue") for i, j in attributes.items()}

        return SQSMessage(
            body=message.get("Body", "").encode(),
            message_id=message.get("MessageId"),
            content_type=headers.pop("content-type", None),
            reply_to=headers.pop("reply_to", None) or "",
            headers=headers,
            raw_message=message,
        )

    def _process_message(
        self,
        func: Callable[[SQSMessage], Awaitable[T]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[SQSMessage], Awaitable[T]]:
        if watcher is None:
            watcher = NotPushBackWatcher()

        @wraps(func)
        async def process_wrapper(message: SQSMessage) -> T:
            context = WatcherContext(
                watcher,
                message,
                on_success=delete_message,
                on_max=delete_message,
                connection=self._connection,
            )

            async with context:
                r = await func(message)

                if message.reply_to:
                    await self.publish(
                        message=r or "",
                        queue=message.reply_to,
                        headers={
                            "correlation_id": message.headers.get("correlation_id")
                        },
                    )

                return r

        return process_wrapper

    def handle(
        self,
        queue: Union[str, SQSQueue],
        *,
        wait_interval: int = 1,
        max_messages_number: int = 10,  # 1...10
        attributes: Sequence[str] = (),
        message_attributes: Sequence[str] = (),
        request_attempt_id: Optional[str] = None,
        visibility_timeout: int = 0,
        dependencies: Sequence[Depends] = (),
        description: str = "",
        **original_kwargs: AnyDict,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[Any, bool], Awaitable[T_HandlerReturn]],
    ]:
        super().handle()

        if isinstance(queue, str):
            queue = SQSQueue(queue)

        self.__max_queue_len = max((self.__max_queue_len, len(queue.name)))

        params = {
            "WaitTimeSeconds": wait_interval,
            "MaxNumberOfMessages": max_messages_number,
            "AttributeNames": [*attributes],
            "VisibilityTimeout": visibility_timeout,
            "MessageAttributeNames": (
                "content-type",
                "reply_to",
                "correlation_id",
                *message_attributes,
            ),
        }
        if request_attempt_id is not None:
            params["ReceiveRequestAttemptId"] = request_attempt_id

        def wrapper(func: HandlerCallable) -> HandlerCallable:
            func, dependant = self._wrap_handler(
                func,
                queue=queue.name,
                extra_dependencies=dependencies,
                **original_kwargs,
            )
            handler = Handler(
                callback=func,
                queue=queue,
                consumer_params=params,
                _description=description,
                dependant=dependant,
            )
            self.handlers.append(handler)
            return func

        return wrapper

    async def start(self) -> None:
        if self.response_queue:
            self.handle(
                self.response_queue,
                _raw=True,
            )(self._consume_response)

        context.set_local(
            "log_context",
            self._get_log_context(None, ""),
        )

        await super().start()

        for handler in self.handlers:  # pragma: no branch
            c = self._get_log_context(None, handler.queue.name)
            self._log(f"`{handler.callback.__name__}` waiting for messages", extra=c)

            url = await self.create_queue(handler.queue)
            handler.task = asyncio.create_task(self._consume(url, handler))

    async def publish(
        self,
        message: SendableMessage,
        queue: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        delay_seconds: int = 0,  # 0...900
        message_attributes: Optional[Dict[str, Any]] = None,
        message_system_attributes: Optional[Dict[str, Any]] = None,
        # FIFO only
        deduplication_id: Optional[str] = None,
        group_id: Optional[str] = None,
        # broker
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
    ) -> None:
        queue_url = await self.get_queue(queue)

        if callback is True:
            reply_to = reply_to or self.response_queue
            if not reply_to:
                raise ValueError(
                    "You should specify `response_queue` at init or use `reply_to` argument"
                )

        if reply_to:
            correlation_id = str(uuid4())
        else:
            correlation_id = ""

        response_future: Optional["asyncio.Future[DecodedMessage]"]
        if callback is True:
            response_future = asyncio.Future()
            self.response_callbacks[correlation_id] = response_future
        else:
            response_future = None

        params = SM(
            message=message,
            headers=headers or {},
            delay_seconds=delay_seconds,
            message_attributes=message_attributes or {},
            message_system_attributes=message_system_attributes or {},
            deduplication_id=deduplication_id,
            group_id=group_id,
        ).to_params(
            reply_to=reply_to,
            correlation_id=correlation_id,
        )

        await self._connection.send_message(QueueUrl=queue_url, **params)

        if response_future is not None:
            if raise_timeout:
                scope = anyio.fail_after
            else:
                scope = anyio.move_on_after

            msg: Any = None
            with scope(callback_timeout):
                msg = await response_future

            if msg:
                return await self._decode_message(msg)

    async def create_queue(self, queue: SQSQueue) -> QueueUrl:
        url = self._queues.get(queue.name)
        if url is None:  # pragma: no branch
            url = (
                await self._connection.create_queue(
                    QueueName=queue.name,
                    Attributes={
                        i: str(j)
                        for i, j in model_to_dict(
                            queue,
                            exclude={"name", "tags"},
                            by_alias=True,
                            exclude_defaults=True,
                            exclude_unset=True,
                        ).items()
                    },
                    tags=queue.tags,
                )
            ).get("QueueUrl", "")
            self._queues[queue.name] = url
        return url

    async def delete_queue(self, queue: str) -> None:
        await self._connection.delete_queue(QueueUrl=self.get_queue(queue))
        self._queues.pop(queue)

    async def get_queue(self, queue: str) -> QueueUrl:
        url = self._queues.get(queue)
        if url is None:
            url = (await self._connection.get_queue_url(QueueName=queue)).get(
                "QueueUrl", ""
            )
            self._queues[queue] = url
        return url

    async def _consume(self, queue_url: str, handler: Handler) -> NoReturn:
        c = self._get_log_context(None, handler.queue.name)

        connected = True
        with context.scope("queue_url", queue_url):
            while True:
                try:
                    if connected is False:
                        await self.create_queue(handler.queue)

                    r = await self._connection.receive_message(
                        QueueUrl=queue_url,
                        **handler.consumer_params,
                    )

                except Exception as e:
                    if connected is True:
                        self._log(e, logging.WARNING, c, exc_info=e)
                        self._queues.pop(handler.queue.name)
                        connected = False

                    await anyio.sleep(5)

                else:
                    if connected is False:
                        self._log("Connection established", logging.INFO, c)
                        connected = True

                    messages = r.get("Messages", [])
                    has_trash_messages = False
                    for msg in messages:
                        try:
                            await handler.callback(msg, True)
                        except Exception:
                            has_trash_messages = True
                        else:
                            has_trash_messages = False

                    if has_trash_messages is True:
                        await anyio.sleep(
                            handler.consumer_params.get("WaitTimeSeconds", 1.0)
                        )

    async def _consume_response(self, message: SQSMessage):
        correlation_id = message.headers.get("correlation_id")
        if correlation_id is not None:
            callback = self.response_callbacks.pop(correlation_id, None)
            if callback is not None:
                callback.set_result(message)
                return

        raise SkipMessage()

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(queue)-{self.__max_queue_len}s | "
            "%(message_id)-10s "
            "- %(message)s"
        )

    def _get_log_context(
        self, message: Optional[SQSMessage], queue: str
    ) -> Dict[str, Any]:
        context = {
            "queue": queue,
            **super()._get_log_context(message),
        }
        return context


async def delete_message(
    message: SQSMessage, connection: Optional[AioBaseClient]
) -> None:
    if connection:
        await connection.delete_message(
            QueueUrl=context.get_local("queue_url"),
            ReceiptHandle=message.raw_message.get("ReceiptHandle", ""),
        )
