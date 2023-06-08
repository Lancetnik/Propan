from propan import PropanApp, RedisBroker
from propan.cli.docs.gen import gen_app_schema_json


def test_server_info():
    schema = gen_app_schema_json(PropanApp(RedisBroker()))
    assert schema["servers"]["dev"] == {
        "protocol": "redis",
        "url": "redis://localhost:6379",
    }
