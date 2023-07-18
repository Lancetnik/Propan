from dataclasses import dataclass, field
from typing import Optional

import aio_pika

from propan.broker.handler import AsyncHandler
from propan.broker.types import AsyncDecoder, AsyncParser
from propan.rabbit.helpers import AioPikaParser, RabbitDeclarer
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.types import AnyDict


@dataclass
class Handler(AsyncHandler[aio_pika.IncomingMessage]):
    queue: RabbitQueue
    exchange: Optional[RabbitExchange] = field(default=None)
    consume_args: AnyDict = field(default_factory=dict)

    _consumer_tag: Optional[str] = field(default=None)
    _queue_obj: Optional[aio_pika.RobustQueue] = field(default=None)

    def __init__(
        self,
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
        consume_args: Optional[AnyDict] = None,
        custom_parser: Optional[AsyncParser[aio_pika.IncomingMessage]] = None,
        custom_decoder: Optional[AsyncDecoder[aio_pika.IncomingMessage]] = None,
    ):
        super().__init__(
            custom_parser=custom_parser,
            custom_decoder=custom_decoder,
        )

        self.queue = queue
        self.exchange = exchange
        self.consume_args = consume_args or {}

        self._consumer_tag = None
        self._queue_obj = None

    async def consume(self, msg: aio_pika.IncomingMessage) -> None:
        if self.custom_parser is not None:
            message = await self.custom_parser(msg, AioPikaParser.parse_message)
        else:
            message = await AioPikaParser.parse_message(msg)

        if self.custom_decoder is not None:
            message.decoded_body = await self.custom_decoder(
                message, AioPikaParser.decode_message
            )
        else:
            message.decoded_body = await AioPikaParser.decode_message(message)

        return await super().consume(message)

    async def start(self, declarer: RabbitDeclarer) -> None:
        self._queue_obj = queue = await declarer.declare_queue(self.queue)

        if self.exchange is not None and self.exchange.name != "default":
            exchange = await declarer.declare_exchange(self.exchange)
            await queue.bind(
                exchange,
                routing_key=self.queue.routing,
                arguments=self.queue.bind_arguments,
            )

        self._consumer_tag = await queue.consume(
            self.consume,
            arguments=self.consume_args,
        )

    async def close(self) -> None:
        if self._queue_obj is not None:
            await self._queue_obj.cancel(self._consumer_tag)
            self._queue_obj = None
