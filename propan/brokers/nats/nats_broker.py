import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

import nats
from nats.aio.client import Client
from nats.aio.msg import Msg
from propan.brokers.model import BrokerUsecase, ContentTypes
from propan.brokers.nats.schemas import Handler
from propan.brokers.push_back_watcher import BaseWatcher
from propan.types import DecoratedCallable
from propan.utils.context.main import log_context


class NatsBroker(BrokerUsecase):
    handlers: List[Handler]
    _connection: Optional[Client]

    __max_queue_len: int
    __max_subject_len: int

    def __init__(self, *args: Any, log_fmt: Optional[str] = None, **kwargs: Any):
        super().__init__(*args, log_fmt=log_fmt, **kwargs)

        self._connection = None

        self.__max_queue_len = 0
        self.__max_subject_len = 4

    async def _connect(self, *args: Any, **kwargs: Any) -> Client:
        return await nats.connect(*args, **kwargs)

    def handle(
        self, subject: str, queue: str = "", *, retry: Union[bool, int] = False
    ) -> Callable[[DecoratedCallable], None]:
        i = len(subject)
        if i > self.__max_subject_len:
            self.__max_subject_len = i

        i = len(queue)
        if i > self.__max_queue_len:
            self.__max_queue_len = i

        parent = super()

        def wrapper(func: DecoratedCallable) -> None:
            for handler in self.handlers:
                if handler.subject == subject and handler.queue == queue:
                    raise ValueError(
                        f"`{func.__name__}` uses already "
                        f"using `{subject}` subject with "
                        f"`{queue}` queue"
                    )

            func = parent._wrap_handler(func, retry, queue=queue, subject=subject)
            handler = Handler(callback=func, subject=subject, queue=queue)
            self.handlers.append(handler)

        return wrapper

    async def start(self) -> None:
        await super().start()

        for handler in self.handlers:
            func = handler.callback

            if self.logger:
                self._get_log_context(None, handler.subject, handler.queue)
                self.logger.info(f"`{func.__name__}` waiting for messages")

            sub = await self._connection.subscribe(handler.subject, cb=func)
            handler.subscription = sub

    async def publish_message(
        self, message: Union[str, Dict[str, Any]], subject: str, **publish_args: Any
    ) -> None:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        if isinstance(message, dict):
            message = json.dumps(message)
            headers = {
                **publish_args.pop("headers", {}),
                "content-type": ContentTypes.json.value,
            }
        else:
            headers = {
                **publish_args.pop("headers", {}),
                "content-type": ContentTypes.text.value,
            }

        return await self._connection.publish(
            subject, message.encode(), headers=headers, **publish_args
        )

    async def close(self) -> None:
        for h in self.handlers:
            await h.subscription.unsubscribe()

        if self._connection:
            await self._connection.drain()

    def _get_log_context(
        self, message: Optional[Msg], subject: str, queue: str = "", **kwargs
    ) -> Dict[str, Any]:
        if message is not None:
            message_id = message.reply or uuid4().hex
            message.message_id = message_id

        context = {
            "subject": subject,
            "queue": queue,
            "message_id": message.message_id[:10] if message else "",
        }

        log_context.set(context)
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

    @staticmethod
    async def _decode_message(message: Msg) -> Union[str, dict, bytes]:
        body = message.data
        if message.header:
            content_type = message.header.get("content-type", "")
            if ContentTypes.json.value in content_type:
                body = json.loads(body.decode())
            elif ContentTypes.text.value in content_type:
                body = body.decode()
        return body

    @staticmethod
    def _process_message(
        func: DecoratedCallable, watcher: Optional[BaseWatcher] = None
    ) -> Callable[[Msg], Any]:
        @wraps(func)
        async def wrapper(message: Msg):
            return await func(message)

        return wrapper
