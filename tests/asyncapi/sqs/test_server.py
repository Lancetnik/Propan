from propan import PropanApp, SQSBroker
from propan.cli.docs.gen import gen_app_schema_json


def test_server_info():
    schema = gen_app_schema_json(PropanApp(SQSBroker()))
    assert schema["servers"]["dev"] == {
        "protocol": "sqs",
        "url": "http://localhost:9324/",
    }
