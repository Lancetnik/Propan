from uuid import uuid4

import pytest
from fastapi import FastAPI

from propan.fastapi import RabbitRouter, RedisRouter
from propan.test import TestRabbitBroker, TestRedisBroker


@pytest.mark.asyncio
async def test_rabbit():
    name = str(uuid4())
    name2 = name + "1"

    router = RabbitRouter("amqp://guest:guest@localhost:5672")
    router.broker = TestRabbitBroker(router.broker)

    app = FastAPI()
    app.include_router(router)

    @router.event(name)
    async def hello():
        return "1"

    @router.event(name2)
    async def hello2(b: int):
        return "2"

    await router.startup()

    r = await router.broker.publish("", queue=name, callback=True, callback_timeout=0.5)
    assert r == "1"

    r = await router.broker.publish(
        "2", queue=name2, callback=True, callback_timeout=0.5
    )
    assert r == "2"

    await router.shutdown()


@pytest.mark.asyncio
async def test_redis():
    name = str(uuid4())
    name2 = name + "1"

    router = RedisRouter()
    router.broker = TestRedisBroker(router.broker)

    app = FastAPI()
    app.include_router(router)

    @router.event(name)
    async def hello():
        return "1"

    @router.event(name2)
    async def hello2(b: int):
        return "2"

    await router.startup()

    r = await router.broker.publish("", name, callback=True, callback_timeout=0.5)
    assert r == "1"

    r = await router.broker.publish("2", name2, callback=True, callback_timeout=0.5)
    assert r == "2"

    await router.shutdown()
