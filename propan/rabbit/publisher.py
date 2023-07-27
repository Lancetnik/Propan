from dataclasses import dataclass
from typing import Optional, Union

import aiormq

from propan.rabbit.helpers import AioPikaPublisher
from propan.rabbit.shared.publisher import Publisher as BasePub
from propan.rabbit.types import AioPikaSendableMessage
from propan.types import AnyDict, DecodedMessage


@dataclass
class Publisher(BasePub):
    _publisher: Optional[AioPikaPublisher] = None

    async def publish(
        self,
        message: AioPikaSendableMessage = "",
        *,
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        **message_kwargs: AnyDict,
    ) -> Union[aiormq.abc.ConfirmationFrameType, DecodedMessage, None]:
        return await self._publisher.publish(
            message=message,
            queue=self.queue,
            exchange=self.exchange,
            routing_key=self.routing_key,
            mandatory=self.mandatory,
            immediate=self.immediate,
            timeout=self.timeout,
            rpc=rpc,
            rpc_timeout=rpc_timeout,
            raise_timeout=raise_timeout,
            persist=self.persist,
            reply_to=self.reply_to,
            **self.message_kwargs,
            **message_kwargs,
        )
