from dataclasses import dataclass, field
from typing import Optional

from propan.kafka.producer import AioKafkaPropanProducer
from propan.kafka.shared.publisher import ABCPublisher
from propan.types import DecodedMessage, SendableMessage


@dataclass
class LogicPublisher(ABCPublisher):
    _producer: Optional[AioKafkaPropanProducer] = field(default=None, init=False)

    async def publish(
        self,
        message: SendableMessage = "",
        *,
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        correlation_id: str = "",
    ) -> Optional[DecodedMessage]:
        return await self._producer.publish(
            message=message,
            topic=self.topic,
            key=self.key,
            partition=self.partition,
            timestamp_ms=self.timestamp_ms,
            headers={
                "correlation_id": correlation_id,
                **(self.headers or {}),
            },
            reply_to=self.reply_to,
            rpc=rpc,
            rpc_timeout=rpc_timeout,
            raise_timeout=raise_timeout,
        )
