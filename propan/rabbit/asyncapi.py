from abc import abstractmethod
from typing import List, Optional, Tuple

from fast_depends.core import build_call_model

from propan.asyncapi import (
    Channel,
    ChannelBinding,
    CorrelationId,
    Message,
    Operation,
    OperationBinding,
)
from propan.asyncapi.message import get_response_schema, parse_handler_params
from propan.asyncapi.schema.bindings import amqp
from propan.rabbit.handler import Handler as BaseHandler
from propan.rabbit.publisher import Publisher as BasePublisher
from propan.rabbit.shared.schemas import ExchangeType, RabbitExchange
from propan.types import AnyDict


class RMQAsyncAPIChannel:
    @abstractmethod
    def get_payloads(self) -> List[AnyDict]:
        raise NotImplementedError()

    def schema(self) -> Tuple[str, Channel]:
        name, _ = super().schema()

        payloads = self.get_payloads()
        assert payloads, "You should use this object at least once"

        return name, Channel(
            description=self.description,
            subscribe=Operation(
                bindings=OperationBinding(
                    amqp=amqp.OperationBinding(
                        cc=self.queue.name,
                    ),
                )
                if _is_exchange(self.exchange)
                else None,
                message=Message(
                    title=f"{name}Message",
                    payload=payloads[0]
                    if len(payloads) == 1
                    else {"oneOf": {body["title"]: body for body in payloads}},
                    correlationId=CorrelationId(
                        location="$message.header#/correlation_id"
                    ),
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


class Publisher(RMQAsyncAPIChannel, BasePublisher):
    def get_payloads(self) -> Tuple[str, Channel]:
        payloads = []
        for call in self.calls:
            call_model = build_call_model(call)
            body = get_response_schema(
                call_model,
                prefix=call_model.call_name.replace("_", " ").title().replace(" ", ""),
            )
            payloads.append(body)

        return payloads


class Handler(RMQAsyncAPIChannel, BaseHandler):
    def get_payloads(self) -> Tuple[str, Channel]:
        payloads = []
        for _, _, _, _, _, _, dep in self.calls:
            body = parse_handler_params(dep, prefix=self.name)
            payloads.append(body)

        return payloads


def _is_exchange(exchange: Optional[RabbitExchange]) -> bool:
    if exchange and exchange.type in (
        ExchangeType.FANOUT.value,
        ExchangeType.HEADERS.value,
    ):
        return False
    return True
