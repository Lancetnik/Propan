from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.kafka import KafkaBroker
from tests.asyncapi.base.subscriber_naming import SubscriberNamingTestCase


class TestNaming(SubscriberNamingTestCase):
    broker_class = KafkaBroker

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
                    "bindings": {"kafka": {"bindingVersion": "0.4.0", "topic": "test"}},
                    "servers": ["development"],
                    "subscribe": {
                        "message": {"$ref": "#/components/messages/HandleMessage"}
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
                    "protocol": "kafka",
                    "protocolVersion": "auto",
                    "url": "localhost",
                }
            },
        }
