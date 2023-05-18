import pytest
from propan.test import TestRedisBroker

from main import broker

@pytest.fixture()
def test_broker():
    async with TestRedisBroker(broker) as b:
        await b.start()
        yield b

def test_publish(test_broker):
    r = await test_broker.publish("ping", queue="ping", callback=True)
    assert r == "pong"