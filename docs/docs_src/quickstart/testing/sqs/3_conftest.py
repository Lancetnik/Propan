import pytest
from propan.test import TestSQSBroker

from main import broker

@pytest.fixture()
def test_broker():
    async with TestSQSBroker(broker) as b:
        await b.start()
        yield b

def test_publish(test_broker):
    r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"