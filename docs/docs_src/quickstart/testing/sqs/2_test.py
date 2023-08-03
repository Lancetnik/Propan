from propan.test import TestSQSBroker

from main import broker

async def test_publish():
    async with TestSQSBroker(broker) as test_broker:
        r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"