from functools import wraps
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
        i = len(subject)
        if i > self.__max_subject_len:
            self.__max_subject_len = i

        i = len(queue)
        if i > self.__max_queue_len:
            self.__max_queue_len = i

        def wrapper(func: DecoratedCallable) -> None:
            for handler in self.handlers:
                if handler.subject == subject and handler.queue == queue:
                    raise ValueError(
                        f"`{func.__name__}` uses already "
                        f"using `{subject}` subject with "
                        f"`{queue}` queue"
                    )

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
        **publish_args: Any,
    ) -> None:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        msg, content_type = self._encode_message(message)

        return await self._connection.publish(
            subject,
            msg,
            headers={
                **publish_args.pop("headers", {}),
                "content-type": content_type,
            },
            **publish_args,
        )

    async def close(self) -> None:
        for h in self.handlers:
            await h.subscription.unsubscribe()

        if self._connection:
            await self._connection.drain()

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
            body=message.dat,
            content_type=message.header.get("content-type", ""),
            headers=message.header,
            raw_message=message,
        )

    def _process_message(
        self, func: Callable[[PropanMessage], T], watcher: Optional[BaseWatcher] = None
    ) -> Callable[[PropanMessage], T]:
        @wraps(func)
        async def wrapper(message: PropanMessage) -> T:
            return await func(message)

        return wrapper
