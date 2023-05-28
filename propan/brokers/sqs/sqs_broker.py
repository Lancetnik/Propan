import asyncio
import logging
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import (
    BaseWatcher,
    FakePushBackWatcher,
    WatcherContext,
)
from propan.brokers.sqs.schema import Handler, SQSQueue
from propan.types import AnyCallable, DecoratedCallable, HandlerWrapper, SendableMessage
from propan.utils import context

T = TypeVar("T")
QueueUrl: TypeAlias = str


class SQSBroker(BrokerUsecase):
    _connection: AioBaseClient
    _queues: Dict[str, QueueUrl]
    handlers: List[Handler]
    __max_queue_len: int

    def __init__(
        self,
        url: str = "http://localhost:9324/",
        *,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(url, log_fmt=log_fmt, **kwargs)
        self._queues = {}
        self.__max_queue_len = 4

    async def _connect(self, url: Optional[str] = None, **kwargs: Any) -> AioBaseClient:
        session = get_session()
        client: AioBaseClient = await session._create_client(
            service_name="sqs", endpoint_url=url, **kwargs
        )
        context.set_global("client", client)
        await client.__aenter__()
        return client

    async def close(self) -> None:
        for h in self.handlers:
            if h.task is not None:
                h.task.cancel()
                h.task = None

        if self._connection is not None:
            await self._connection.__aexit__(None, None, None)
            self._connection = None

    async def _parse_message(self, message: Dict[str, Any]) -> PropanMessage:
        attributes = message.get("MessageAttributes", {})

        headers = {}
        for i, j in attributes.items():
            v = j.get("StringValue", "0")
            if v != "0":
                headers[i] = v
            else:
                headers[i] = None

        return PropanMessage(
            body=message.get("Body", "").encode(),
            message_id=message.get("MessageId"),
            content_type=headers.pop("content-type", None),
            reply_to=headers.pop("reply", None) or "",
            headers=headers,
            raw_message=message,
        )

    def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]:
        if watcher is None:
            watcher = FakePushBackWatcher()

        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            context = WatcherContext(
                watcher,
                message.message_id,
                on_success=self.delete_message,
                on_max=self.delete_message,
            )

            async with context:
                r = await func(message)

                if message.reply_to:
                    await self.publish(r or "", message.reply_to)

                return r

        return wrapper

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
        retry: Union[bool, int] = False,
    ) -> HandlerWrapper:
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
                "reply",
                *message_attributes,
            ),
        }
        if request_attempt_id is not None:
            params["ReceiveRequestAttemptId"] = request_attempt_id

        def wrapper(func: AnyCallable) -> DecoratedCallable:
            func = self._wrap_handler(func, queue=queue.name, retry=retry)
            handler = Handler(callback=func, queue=queue, consumer_params=params)
            self.handlers.append(handler)
            return func

        return wrapper

    async def start(self) -> None:
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
    ) -> Any:
        queue_url = await self.get_queue(queue)

        params = self._build_message(
            message=message,
            queue_url=queue_url,
            headers=headers,
            delay_seconds=delay_seconds,
            message_attributes=message_attributes,
            message_system_attributes=message_system_attributes,
            deduplication_id=deduplication_id,
            group_id=group_id,
            reply_to=reply_to,
        )

        await self._connection.send_message(**params)

    @classmethod
    def _build_message(
        cls,
        message: SendableMessage,
        queue_url: str,
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
    ) -> Dict[str, Any]:
        msg, content_type = cls._encode_message(message)

        headers = headers or {}
        headers["content-type"] = headers.get("content-type", content_type)
        headers["reply"] = reply_to

        params = {
            "QueueUrl": queue_url,
            "MessageBody": msg.decode(),
            "DelaySeconds": delay_seconds,
            "MessageSystemAttributes": message_system_attributes or {},
            "MessageAttributes": {
                **(message_attributes or {}),
                **{
                    i: {
                        "StringValue": j or "0",
                        "DataType": "String",
                    }
                    for i, j in headers.items()
                },
            },
        }

        if deduplication_id is not None:
            params["MessageDeduplicationId"] = deduplication_id

        if group_id is not None:
            params["MessageGroupId"] = group_id

        return params

    async def create_queue(self, queue: SQSQueue) -> QueueUrl:
        url = self._queues.get(queue.name)
        if url is None:  # pragma: no branch
            url = (
                await self._connection.create_queue(
                    QueueName=queue.name,
                    Attributes={
                        i: str(j)
                        for i, j in queue.dict(
                            exclude={"name"}, by_alias=True, exclude_defaults=True
                        ).items()
                    },
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

    async def delete_message(self) -> None:
        message = context.get_local("message")
        await self._connection.delete_message(
            QueueUrl=context.get_local("queue_url"),
            ReceiptHandle=message.get("ReceiptHandle", ""),
        )

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
                        self._log(e, logging.WARNING, c)
                        self._queues.pop(handler.queue.name)
                        connected = False

                    await asyncio.sleep(5)

                else:
                    if connected is False:
                        self._log("Connection established", logging.INFO, c)
                        connected = True

                    for msg in r.get("Messages", []):
                        await handler.callback(msg)

    @property
    def fmt(self) -> str:
        return self._fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(queue)-{self.__max_queue_len}s | "
            "%(message_id)-10s "
            "- %(message)s"
        )

    def _get_log_context(
        self, message: Optional[PropanMessage], queue: str
    ) -> Dict[str, Any]:
        context = {
            "queue": queue,
            **super()._get_log_context(message),
        }
        return context
