import pytest
from propan.test import TestKafkaBroker

from main import broker

@pytest.fixture()
async def test_broker():
    async with TestKafkaBroker(broker) as b:
        yield b

async def test_publish(test_broker):
    r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"