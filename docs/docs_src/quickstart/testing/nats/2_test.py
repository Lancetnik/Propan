from propan.test import TestNatsBroker

from main import broker

def test_publish():
    async with TestNatsBroker(broker) as test_broker:
        await test_broker.start()
        r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"