from typing import Dict, Optional, Union

from propan._compat import model_copy
from propan.rabbit.asyncapi import Publisher
from propan.rabbit.shared.router import RabbitRouter as BaseRouter
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue, get_routing_hash
from propan.rabbit.shared.types import TimeoutType
from propan.types import AnyDict


class RabbitRouter(BaseRouter):
    _publishers: Dict[int, Publisher]

    def publisher(
        self,
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ) -> Publisher:
        q = RabbitQueue.validate(queue)
        q = model_copy(q, update={"name": self.prefix + q.name})
        ex = RabbitExchange.validate(exchange)
        key = get_routing_hash(q, ex)
        publisher = self._publishers[key] = self._publishers.get(
            key,
            Publisher(
                queue=q,
                exchange=ex,
                routing_key=routing_key,
                mandatory=mandatory,
                immediate=immediate,
                timeout=timeout,
                persist=persist,
                reply_to=reply_to,
                message_kwargs=message_kwargs,
            ),
        )
        return publisher
