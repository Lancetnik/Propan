from propan.test import TestRedisBroker

from main import broker

async def test_publish():
    async with TestRedisBroker(broker) as test_broker:
        r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"