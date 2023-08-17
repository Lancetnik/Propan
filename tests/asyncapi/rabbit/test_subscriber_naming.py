from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.rabbit import RabbitBroker
from tests.asyncapi.base.subscriber_naming import SubscriberNamingTestCase


class TestNaming(SubscriberNamingTestCase):
    broker_class = RabbitBroker

    def test_base(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle():
            ...

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
                                "name": "test",
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
                                "cc": "test",
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
                        "payload": {"$ref": "#/components/schemas/Payload"},
                        "title": "HandleMessage",
                    }
                },
                "schemas": {"Payload": {"title": "Payload", "type": "null"}},
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
