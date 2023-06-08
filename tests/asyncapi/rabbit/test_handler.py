from propan import PropanApp, RabbitBroker
from propan.brokers.rabbit import ExchangeType, RabbitExchange
from propan.cli.docs.gen import gen_app_schema_json


def test_base_handler():
    broker = RabbitBroker()

    @broker.handle("test")
    async def handler(a: int):
        ...

    schema = gen_app_schema_json(PropanApp(broker))

    assert schema["channels"] == {
        "Handler": {
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
            "servers": ["dev"],
            "subscribe": {
                "bindings": {
                    "amqp": {"ack": True, "bindingVersion": "0.2.0", "cc": "test"}
                },
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }


def test_fanout_exchange_handler():
    broker = RabbitBroker()

    @broker.handle("test", RabbitExchange("test", type=ExchangeType.FANOUT))
    async def handler(a: int):
        """Test description"""
        ...

    schema = gen_app_schema_json(PropanApp(broker))
    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "amqp": {
                    "bindingVersion": "0.2.0",
                    "exchange": {
                        "autoDelete": False,
                        "durable": False,
                        "name": "test",
                        "type": "fanout",
                        "vhost": "/",
                    },
                    "is": "routingKey",
                }
            },
            "servers": ["dev"],
            "subscribe": {
                "bindings": {"amqp": {"ack": True, "bindingVersion": "0.2.0"}},
                "description": "Test description",
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }


def test_direct_exchange_handler():
    broker = RabbitBroker()

    @broker.handle("test", RabbitExchange("test"), description="Test description")
    async def handler(a: int):
        ...

    schema = gen_app_schema_json(PropanApp(broker))
    assert schema["channels"] == {
        "Handler": {
            "bindings": {
                "amqp": {
                    "bindingVersion": "0.2.0",
                    "exchange": {
                        "autoDelete": False,
                        "durable": False,
                        "name": "test",
                        "type": "direct",
                        "vhost": "/",
                    },
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
            "servers": ["dev"],
            "subscribe": {
                "bindings": {
                    "amqp": {"ack": True, "bindingVersion": "0.2.0", "cc": "test"}
                },
                "description": "Test description",
                "message": {"$ref": "#/components/messages/HandlerMessage"},
            },
        }
    }
