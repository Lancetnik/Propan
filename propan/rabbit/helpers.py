from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any, Dict, Optional, Type, Union
from uuid import uuid4

import aio_pika
import aiormq
import anyio
from aio_pika.abc import DeliveryMode
from anyio.streams.memory import MemoryObjectReceiveStream

from propan._compat import model_to_dict
from propan.broker.parsers import decode_message, encode_message
from propan.broker.types import AsyncCustomDecoder, AsyncCustomParser
from propan.exceptions import WRONG_PUBLISH_ARGS
from propan.rabbit.message import RabbitMessage
from propan.rabbit.shared.constants import RABBIT_REPLY
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
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
            q = await self.channel.declare_queue(
                **model_to_dict(queue, exclude={"routing_key"})
            )
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
            content_type=message.content_type,
            message_id=message.message_id or str(uuid4()),
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


class AioPikaPublisher:
    _channel: aio_pika.RobustChannel
    _rpc_lock: anyio.Lock
    _decoder: AsyncCustomDecoder[aio_pika.IncomingMessage]
    _parser: AsyncCustomParser[aio_pika.IncomingMessage]
    declarer: RabbitDeclarer

    def __init__(
        self,
        channel: aio_pika.RobustChannel,
        declarer: RabbitDeclarer,
        global_parser: Optional[AsyncCustomParser[aio_pika.IncomingMessage]] = None,
        global_decoder: Optional[AsyncCustomDecoder[aio_pika.IncomingMessage]] = None,
    ):
        self._channel = channel
        self.declarer = declarer
        self._parser = global_parser or AioPikaParser.parse_message
        self._decoder = global_decoder or AioPikaParser.decode_message
        self._rpc_lock = anyio.Lock()

    async def publish(
        self,
        message: AioPikaSendableMessage = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Union[aiormq.abc.ConfirmationFrameType, DecodedMessage, None]:
        p_queue = RabbitQueue.validate(queue)

        if rpc is True:
            if reply_to is not None:
                raise WRONG_PUBLISH_ARGS
            else:
                context = RPCCallback(
                    self._rpc_lock, self.declarer.queues[RABBIT_REPLY]
                )
        else:
            context = fake_context()

        async with context as response_queue:
            r = await self._publish(
                message=message,
                exchange=exchange,
                routing_key=routing_key or p_queue.routing or "",
                mandatory=mandatory,
                immediate=immediate,
                timeout=timeout,
                persist=persist,
                reply_to=RABBIT_REPLY if response_queue else reply_to,
                **message_kwargs,
            )

            if response_queue is None:
                return r

            else:
                if raise_timeout:
                    scope = anyio.fail_after
                else:
                    scope = anyio.move_on_after

                msg: Any = None
                with scope(rpc_timeout):
                    msg = await response_queue.receive()

                if msg:
                    msg = await self._parser(msg)
                    return await self._decoder(msg)

    async def _publish(
        self,
        message: AioPikaSendableMessage = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Union[aiormq.abc.ConfirmationFrameType, DecodedMessage, None]:
        p_exchange = RabbitExchange.validate(exchange)

        if p_exchange is None:
            exchange_obj = self._channel.default_exchange
        else:
            exchange_obj = await self.declarer.declare_exchange(p_exchange)

        message = AioPikaParser.encode_message(
            message=message,
            persist=persist,
            reply_to=reply_to,
            **message_kwargs,
        )

        return await exchange_obj.publish(
            message=message,
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
        )


@asynccontextmanager
async def fake_context() -> None:
    yield None
