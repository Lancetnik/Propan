import pytest
from propan.test import TestRabbitBroker

from main import broker

@pytest.fixture()
async def test_broker():
    async with TestRabbitBroker(broker) as b:
        yield b

async def test_publish(test_broker):
    r = await test_broker.publish("ping", "ping", callback=True)
    assert r == "pong"