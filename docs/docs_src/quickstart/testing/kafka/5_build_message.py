from propan.test.kafka import build_message

from main import healthcheck

def test_publish(test_broker):
    msg = build_message("ping", "ping")
    assert (await healthcheck(msg)) == "pong"