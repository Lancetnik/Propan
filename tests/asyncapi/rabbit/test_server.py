from propan import PropanApp, RabbitBroker
from propan.cli.docs.gen import get_schema_json


def test_server_info():
    schema = get_schema_json(PropanApp(RabbitBroker()))
    assert schema["servers"]["dev"] == {
        "protocol": "amqp",
        "url": "amqp://guest:guest@localhost:5672/",
        "protocolVersion": "0.9.1",
    }


def test_server_custom_info():
    schema = get_schema_json(
        PropanApp(
            RabbitBroker(
                "amqps://rabbithost.com", protocol="amqps", protocol_version="0.8.0"
            )
        )
    )
    assert schema["servers"]["dev"] == {
        "protocol": "amqps",
        "url": "amqps://rabbithost.com",
        "protocolVersion": "0.8.0",
    }
