from dataclasses import dataclass, field
from typing import Optional

from propan.kafka.helpers import AioKafkaPublisher
from propan.kafka.shared.publisher import Publisher as BasePub
from propan.types import DecodedMessage, SendableMessage


@dataclass
class Publisher(BasePub):
    _publisher: Optional[AioKafkaPublisher] = field(default=None)

    async def publish(
        self,
        message: SendableMessage = "",
        *,
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        correlation_id: str = "",
    ) -> Optional[DecodedMessage]:
        return await self._publisher.publish(
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
