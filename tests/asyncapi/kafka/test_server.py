from propan import KafkaBroker, PropanApp
from propan.cli.docs.gen import get_schema_json


def test_server_info():
    schema = get_schema_json(PropanApp(KafkaBroker()))
    assert schema["servers"]["dev"] == {
        "protocol": "kafka",
        "url": "localhost",
        "protocolVersion": "auto",
    }


def test_server_custom_info():
    schema = get_schema_json(
        PropanApp(
            KafkaBroker(
                "kafka:9092",
                protocol="kafka-secury",
                api_version="1.0.0",
            )
        )
    )
    assert schema["servers"]["dev"] == {
        "protocol": "kafka-secury",
        "url": "kafka:9092",
        "protocolVersion": "1.0.0",
    }
