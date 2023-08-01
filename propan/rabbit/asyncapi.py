from typing import Tuple, Optional

from propan.asyncapi import (
    Channel,
    Subscription,
    OperationBinding,
    ChannelBinding,
    Message,
)
from propan.asyncapi.schema.bindings import amqp
from propan.rabbit.shared.schemas import RabbitExchange, ExchangeType
from propan.rabbit.handler import Handler as BaseHandler


class Handler(BaseHandler):
    def schema(self) -> Tuple[str, Channel]:
        name, _ = super().schema()
        return name, Channel(
            subscribe=Subscription(
                description=self.description,
                bindings=OperationBinding(
                    amqp=amqp.OperationBinding(
                        cc=self.queue.name if _is_exchange(self.exchange) else None,
                    ),
                ),
                message=Message(
                    payload={}
                ),
            ),
            bindings=ChannelBinding(
                amqp=amqp.ChannelBinding(
                    **{
                        "is": "routingKey",  # type: ignore
                        "queue": amqp.Queue(
                            name=self.queue.name,
                            durable=self.queue.durable,
                            exclusive=self.queue.exclusive,
                            autoDelete=self.queue.auto_delete,
                        )
                        if _is_exchange(self.exchange)
                        else None,
                        "exchange": (
                            amqp.Exchange(type="default")
                            if self.exchange is None
                            else amqp.Exchange(
                                type=self.exchange.type,  # type: ignore
                                name=self.exchange.name,
                                durable=self.exchange.durable,
                                autoDelete=self.exchange.auto_delete,
                            )
                        ),
                    }
                )
            ),
    )


def _is_exchange(exchange: Optional[RabbitExchange]) -> bool:
    if exchange and exchange.type in (
        ExchangeType.FANOUT.value,
        ExchangeType.HEADERS.value,
    ):
        return False
    return True
