from typing import Dict

from fast_depends.core import build_call_model

from propan.asyncapi.base import AsyncAPIOperation
from propan.asyncapi.message import get_response_schema, parse_handler_params
from propan.asyncapi.schema import (
    Channel,
    ChannelBinding,
    CorrelationId,
    Message,
    Operation,
)
from propan.asyncapi.schema.bindings import kafka
from propan.kafka.handler import LogicHandler
from propan.kafka.publisher import LogicPublisher


class Handler(LogicHandler, AsyncAPIOperation):
    def schema(self) -> Dict[str, Channel]:
        payloads = []
        for _, _, _, _, _, _, dep in self.calls:
            body = parse_handler_params(dep, prefix=self.name)
            payloads.append(body)

        channels = {}

        for t in self.topics:
            channels[f"{self.name}{t}"] = Channel(
                description=self.description,
                subscribe=Operation(
                    message=Message(
                        title=f"{self.name}Message",
                        payload=payloads[0]
                        if len(payloads) == 1
                        else {"oneOf": {body["title"]: body for body in payloads}},
                        correlationId=CorrelationId(
                            location="$message.header#/correlation_id"
                        ),
                    ),
                ),
                bindings=ChannelBinding(kafka=kafka.ChannelBinding(topic=t)),
            )

        return channels


class Publisher(LogicPublisher, AsyncAPIOperation):
    @property
    def name(self) -> str:
        return self.title or "undefined"

    def schema(self) -> Dict[str, Channel]:
        payloads = []
        for call in self.calls:
            call_model = build_call_model(call)
            body = get_response_schema(
                call_model,
                prefix=call_model.call_name.replace("_", " ").title().replace(" ", ""),
            )
            payloads.append(body)

        return {
            f"{self.name}{self.topic}": Channel(
                description=self.description,
                publish=Operation(
                    message=Message(
                        title=f"{self.name}Message",
                        payload=payloads[0]
                        if len(payloads) == 1
                        else {"oneOf": {body["title"]: body for body in payloads}},
                        correlationId=CorrelationId(
                            location="$message.header#/correlation_id"
                        ),
                    ),
                ),
                bindings=ChannelBinding(kafka=kafka.ChannelBinding(topic=self.topic)),
            )
        }
