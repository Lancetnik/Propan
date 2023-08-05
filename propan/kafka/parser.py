from uuid import uuid4

import aiokafka

from propan.broker.parsers import decode_message
from propan.kafka.message import KafkaMessage
from propan.types import DecodedMessage


class AioKafkaParser:
    @staticmethod
    async def parse_message(
        message: aiokafka.ConsumerRecord,
    ) -> KafkaMessage:
        headers = {i: j.decode() for i, j in message.headers}
        return KafkaMessage(
            body=message.value,
            headers=headers,
            reply_to=headers.get("reply_to", ""),
            content_type=headers.get("content-type"),
            message_id=f"{message.offset}-{message.timestamp}",
            correlation_id=headers.get("correlation_id", str(uuid4())),
            raw_message=message,
        )

    @staticmethod
    async def decode_message(msg: KafkaMessage) -> DecodedMessage:
        return decode_message(msg)
