from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.kafka import KafkaBroker, KafkaRoute, KafkaRouter
from tests.asyncapi.base.arguments import ArgumentsTestcase
from tests.asyncapi.base.publisher import PublisherTestcase
from tests.asyncapi.base.router import RouterTestcase


class TestRouter(RouterTestcase):
    broker_class = KafkaBroker
    router_class = KafkaRouter
    route_class = KafkaRoute

    def test_prefix(self):
        broker = self.broker_class()

        router = self.router_class(prefix="test_")

        @router.subscriber("test")
        async def handle(msg):
            ...

        broker.include_router(router)

        schema = get_app_schema(PropanApp(broker)).to_jsonable()

        assert schema == {
            "asyncapi": "2.6.0",
            "channels": {
                "HandleTestTest": {
                    "bindings": {
                        "kafka": {"bindingVersion": "0.4.0", "topic": "test_test"}
                    },
                    "servers": ["development"],
                    "subscribe": {
                        "message": {
                            "$ref": "#/components/messages/HandleTestTestMessage"
                        }
                    },
                }
            },
            "components": {
                "messages": {
                    "HandleTestTestMessage": {
                        "correlationId": {
                            "location": "$message.header#/correlation_id"
                        },
                        "payload": {
                            "$ref": "#/components/schemas/HandleTestTestMsgPayload"
                        },
                        "title": "HandleTestTestMessage",
                    }
                },
                "schemas": {
                    "HandleTestTestMsgPayload": {"title": "HandleTestTestMsgPayload"}
                },
            },
            "defaultContentType": "application/json",
            "info": {"description": "", "title": "Propan", "version": "0.1.0"},
            "servers": {
                "development": {
                    "protocol": "kafka",
                    "protocolVersion": "auto",
                    "url": "localhost",
                }
            },
        }


class TestRouterArguments(ArgumentsTestcase):
    broker_class = KafkaRouter

    def build_app(self, router):
        broker = KafkaBroker()
        broker.include_router(router)
        return PropanApp(broker)


class TestRouterPublisher(PublisherTestcase):
    broker_class = KafkaRouter

    def build_app(self, router):
        broker = KafkaBroker()
        broker.include_router(router)
        return PropanApp(broker)
