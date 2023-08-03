from propan.test.sqs import build_message

from main import healthcheck

async def test_publish(test_broker):
    msg = build_message("ping", "ping")
    assert (await healthcheck(msg)) == "pong"