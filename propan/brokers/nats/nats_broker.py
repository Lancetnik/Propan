import json
from functools import wraps
from typing import (
    Optional, Callable, Union,
    List, Dict, Any
)
from uuid import uuid4

import nats
from nats.aio.client import Client
from nats.aio.msg import Msg

from propan.log.formatter import expand_log_field
from propan.utils.context.main import log_context
from propan.brokers.model import BrokerUsecase
from propan.brokers.push_back_watcher import BaseWatcher

from propan.brokers.nats.schemas import Handler, JetStream


class NatsBroker(BrokerUsecase):
    handlers: List[Handler] = []
    _connection: Optional[Client] = None

    __max_queue_len = 0
    __max_subject_len = 4

    def __init__(
        self,
        *args,
        log_fmt: Optional[str] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._fmt = log_fmt

    async def __aenter__(self) -> 'NatsBroker':
        await self.connect()
        return self
    
    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def _connect(self, *args, **kwargs) -> Client:
        return await nats.connect(*args, **kwargs)

    def handle(self,
               subject: str,
               queue: str = "",
               retry: Union[bool, int] = False) -> Callable:
        if (i := len(subject)) > self.__max_subject_len:
            self.__max_subject_len = i

        if (i := len(queue)) > self.__max_queue_len:
            self.__max_queue_len = i

        parent = super()

        def wrapper(func) -> None:
            for handler in self.handlers:
                if handler.subject == subject and handler.queue == queue:
                    raise ValueError(f"`{func.__name__}` uses already "
                                     f"using `{subject}` subject with "
                                     f"`{queue}` queue")

            func = parent.handle(func, retry, queue=queue, subject=subject)
            handler = Handler(callback=func, subject=subject, queue=queue)
            self.handlers.append(handler)

        return wrapper

    async def start(self):
        await super().start()

        for handler in self.handlers:
            func = handler.callback            

            if self.logger:
                self._get_log_context(None, handler.subject, handler.queue)
                self.logger.info(f'`{func.__name__}` waiting for messages')

            sub = await self._connection.subscribe(handler.subject, cb=func)
            handler.subscription = sub

    async def publish_message(self,
                              message: Union[str, dict],
                              subject: str,
                              **publish_args) -> None:
        if self._connection is None:
            raise ValueError("NatsConnection not started yet")

        if isinstance(message, dict):
            message = json.dumps(message)
            headers = {
                **publish_args.pop("headers", {}),
                "content-type": "application/json"
            }
        else:
            headers = {
                **publish_args.pop("headers", {}),
                "content-type": "text/plain"
            }

        return await self._connection.publish(subject,
                                              message.encode(),
                                              headers=headers,
                                              **publish_args)

    async def close(self):
        for h in self.handlers:
            await h.subscription.unsubscribe()

        if self._connection:
            await self._connection.drain()

    def _get_log_context(self,
                         message: Optional[Msg],
                         subject: str,
                         queue: str = "",
                         **kwrags) -> Dict[str, Any]:
        if message is not None:
            message_id = message.reply or uuid4().hex
            message.message_id = message_id

        context = {
            "subject": subject,
            "queue": queue,
            "message_id": message.message_id[:10] if message else  ""
        }

        log_context.set(context)
        return context

    @property
    def fmt(self):
        return self._fmt or (
            '%(asctime)s %(levelname)s - '
            f'%(subject)-{self.__max_subject_len}s | ' + 
            (f'%(queue)-{self.__max_queue_len}s | ' if self.__max_queue_len else "") +
            '%(message_id)-10s '
            '- %(message)s'
        )

    @staticmethod
    async def _decode_message(message: Msg) -> Union[str, dict]:
        body = message.data.decode()
        if message.header and message.header.get("content-type") == "application/json":
            body = json.loads(body)
        return body

    @staticmethod
    def _process_message(func: Callable, watcher: Optional[BaseWatcher] = None) -> Callable:
        @wraps(func)
        async def wrapper(message: Msg):
            return await func(message)
        return wrapper
