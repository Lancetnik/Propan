from contextlib import asynccontextmanager
from types import TracebackType
from typing import Dict, Optional, Type, Union
from uuid import uuid4

import aio_pika
import anyio
from aio_pika.abc import DeliveryMode
from anyio.streams.memory import MemoryObjectReceiveStream

from propan._compat import model_to_dict
from propan.broker.parsers import decode_message, encode_message
from propan.rabbit.message import RabbitMessage
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.types import AioPikaSendableMessage
from propan.types import AnyDict, DecodedMessage
from propan.utils.classes import Singleton


class RabbitDeclarer(Singleton):
    channel: aio_pika.RobustChannel
    queues: Dict[Union[RabbitQueue, str], aio_pika.RobustQueue]
    exchanges: Dict[Union[RabbitExchange, str], aio_pika.RobustExchange]

    def __init__(self, channel: aio_pika.RobustChannel) -> None:
        self.channel = channel
        self.queues = {}
        self.exchanges = {}

    async def declare_queue(
        self,
        queue: RabbitQueue,
    ) -> aio_pika.RobustQueue:
        q = self.queues.get(queue)
        if q is None:
            q = await self.channel.declare_queue(**model_to_dict(queue))
            self.queues[queue] = q
        return q

    async def declare_exchange(
        self,
        exchange: RabbitExchange,
    ) -> aio_pika.RobustExchange:
        exch = self.exchanges.get(exchange)

        if exch is None:
            exch = await self.channel.declare_exchange(**model_to_dict(exchange))
            self.exchanges[exchange] = exch

        if exchange.bind_to is not None:
            parent = await self.declare_exchange(exchange.bind_to)
            await exch.bind(
                exchange=parent,
                routing_key=exchange.routing_key,
                arguments=exchange.arguments,
            )

        return exch


class AioPikaParser:
    @staticmethod
    async def parse_message(
        message: aio_pika.IncomingMessage,
    ) -> RabbitMessage:
        return RabbitMessage(
            body=message.body,
            headers=message.headers,
            reply_to=message.reply_to or "",
            message_id=message.message_id,
            content_type=message.content_type or "",
            correlation_id=message.correlation_id or str(uuid4()),
            raw_message=message,
        )

    @staticmethod
    async def decode_message(msg: RabbitMessage) -> DecodedMessage:
        return decode_message(msg)

    @staticmethod
    def encode_message(
        message: AioPikaSendableMessage,
        persist: bool = False,
        callback_queue: Optional[aio_pika.abc.AbstractRobustQueue] = None,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> aio_pika.Message:
        if not isinstance(message, aio_pika.Message):
            message, content_type = encode_message(message)

            delivery_mode = (
                DeliveryMode.PERSISTENT if persist else DeliveryMode.NOT_PERSISTENT
            )

            message = aio_pika.Message(
                message,
                **{
                    "delivery_mode": delivery_mode,
                    "content_type": content_type,
                    "reply_to": callback_queue or reply_to,
                    "correlation_id": str(uuid4()),
                    **message_kwargs,
                },
            )

        return message


class RPCCallback:
    def __init__(self, lock: anyio.Lock, callback_queue: aio_pika.RobustQueue):
        self.lock = lock
        self.queue = callback_queue

    async def __aenter__(self) -> MemoryObjectReceiveStream:
        (
            send_response_stream,
            receive_response_stream,
        ) = anyio.create_memory_object_stream(max_buffer_size=1)
        await self.lock.acquire()

        self.consumer_tag = await self.queue.consume(
            callback=send_response_stream.send,
            no_ack=True,
        )

        return receive_response_stream

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ):
        self.lock.release()
        await self.queue.cancel(self.consumer_tag)


@asynccontextmanager
async def fake_context() -> None:
    yield None
