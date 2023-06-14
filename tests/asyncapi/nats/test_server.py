from propan import NatsBroker, PropanApp
from propan.cli.docs.gen import gen_app_schema_json


def test_server_info():
    schema = gen_app_schema_json(PropanApp(NatsBroker()))
    assert schema["servers"]["dev"] == {
        "protocol": "nats",
        "url": "nats://localhost:4222",
    }
