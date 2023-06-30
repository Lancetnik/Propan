from typing import Optional, Dict, Any

from propan.types import SendableMessage
from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers.redis.schemas import RedisMessage


class RedisProcess(BrokerAsyncUsecase):
    ...
    async def publish(
        self,
        message: SendableMessage = "",
        channel: str = "",
        *,
        reply_to: str = "",
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self._connection is None:
            raise ValueError("Redis connection not established yet")

        msg, content_type = self._encode_message(message)

        await self._connection.publish(
            channel,
            RedisMessage(
                data=msg,
                headers={
                    "content-type": content_type or "",
                    **(headers or {}),
                },
                reply_to=reply_to,
            ).json(),
        )
