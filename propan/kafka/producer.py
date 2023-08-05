from typing import Dict, Optional
from uuid import uuid4

import aiokafka

from propan.broker.parsers import encode_message
from propan.broker.types import AsyncCustomDecoder, AsyncCustomParser
from propan.kafka.parser import AioKafkaParser
from propan.types import DecodedMessage, SendableMessage


class AioKafkaPropanProducer:
    _producer: Optional[aiokafka.AIOKafkaProducer]
    _decoder: AsyncCustomDecoder[aiokafka.ConsumerRecord]
    _parser: AsyncCustomParser[aiokafka.ConsumerRecord]

    def __init__(
        self,
        producer: aiokafka.AIOKafkaProducer,
        global_parser: Optional[AsyncCustomDecoder[aiokafka.ConsumerRecord]] = None,
        global_decoder: Optional[AsyncCustomParser[aiokafka.ConsumerRecord]] = None,
    ):
        self._producer = producer
        self._parser = global_parser or AioKafkaParser.parse_message
        self._decoder = global_decoder or AioKafkaParser.decode_message

    async def publish(
        self,
        message: SendableMessage,
        topic: str,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        reply_to: str = "",
        rpc: bool = False,
        rpc_timeout: Optional[float] = None,
        raise_timeout: bool = False,
    ) -> Optional[DecodedMessage]:
        assert self._producer, "You need to connect broker at first"

        message, content_type = encode_message(message)

        headers_to_send = {
            "content-type": content_type or "",
            **(headers or {}),
        }

        if reply_to:
            correlation_id = str(uuid4())
            headers_to_send.update(
                {
                    "reply_to": reply_to,
                    "correlation_id": correlation_id,
                }
            )
        else:
            correlation_id = ""

        await self._producer.send(
            topic=topic,
            value=message,
            key=key,
            partition=partition,
            timestamp_ms=timestamp_ms,
            headers=[(i, (j or "").encode()) for i, j in headers_to_send.items()],
        )

    async def stop(self):
        if self._producer is not None:
            await self._producer.stop()
