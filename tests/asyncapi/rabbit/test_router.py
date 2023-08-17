from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.rabbit import RabbitBroker, RabbitRoute, RabbitRouter
from tests.asyncapi.base.arguments import ArgumentsTestcase
from tests.asyncapi.base.router import RouterTestcase


class TestRouter(RouterTestcase):
    broker_class = RabbitBroker
    router_class = RabbitRouter
    route_class = RabbitRoute

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
                "Handle": {
                    "bindings": {
                        "amqp": {
                            "bindingVersion": "0.2.0",
                            "exchange": {"type": "default", "vhost": "/"},
                            "is": "routingKey",
                            "queue": {
                                "autoDelete": False,
                                "durable": False,
                                "exclusive": False,
                                "name": "test_test",
                                "vhost": "/",
                            },
                        }
                    },
                    "description": "undefined",
                    "servers": ["development"],
                    "subscribe": {
                        "bindings": {
                            "amqp": {
                                "ack": True,
                                "bindingVersion": "0.2.0",
                                "cc": "test_test",
                            }
                        },
                        "message": {"$ref": "#/components/messages/HandleMessage"},
                    },
                }
            },
            "components": {
                "messages": {
                    "HandleMessage": {
                        "correlationId": {
                            "location": "$message.header#/correlation_id"
                        },
                        "payload": {"$ref": "#/components/schemas/HandleMsgPayload"},
                        "title": "HandleMessage",
                    }
                },
                "schemas": {"HandleMsgPayload": {"title": "HandleMsgPayload"}},
            },
            "defaultContentType": "application/json",
            "info": {"description": "", "title": "Propan", "version": "0.1.0"},
            "servers": {
                "development": {
                    "protocol": "amqp",
                    "protocolVersion": "0.9.1",
                    "url": "amqp://guest:guest@localhost:5672/",
                }
            },
        }


class TestRouterArguments(ArgumentsTestcase):
    broker_class = RabbitRouter

    def build_app(self, router):
        broker = RabbitBroker()
        broker.include_router(router)
        return PropanApp(broker)
