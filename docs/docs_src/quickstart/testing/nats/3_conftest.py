import pytest
from propan.test import TestNatsBroker

from main import broker

@pytest.fixture()
def test_broker():
    async with TestNatsBroker(broker) as b:
        yield b

def test_publish(test_broker):
    r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"