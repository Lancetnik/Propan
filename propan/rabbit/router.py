from typing import List, Optional, Union

from propan._compat import model_copy
from propan.rabbit.publisher import Publisher
from propan.rabbit.shared.router import RabbitRouter as BaseRouter
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.shared.types import TimeoutType
from propan.types import AnyDict


class RabbitRouter(BaseRouter):
    _publishers: List[Publisher]

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
        publisher = Publisher(
            queue=model_copy(q, update={"name": self.prefix + q.name}),
            exchange=RabbitExchange.validate(exchange),
            routing_key=routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout,
            persist=persist,
            reply_to=reply_to,
            message_kwargs=message_kwargs,
        )
        self._publishers.append(publisher)
        return publisher
