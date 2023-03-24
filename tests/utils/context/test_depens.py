import asyncio

import pytest

from propan.brokers import RabbitBroker
from propan.utils.context import Depends, use_context


@pytest.mark.asyncio
async def test_sync_depends():
    key = 1000

    @use_context
    async def func(*args, k = Depends(lambda: key), **kwargs):
        return k is key
    
    assert await func(key=key)


@pytest.mark.asyncio
async def test_async_depends():
    key = 1000

    async def dep():
        return key

    @use_context
    async def func(*args, k = Depends(dep), **kwargs):
        return k is key
    
    assert await func(key=key)


@pytest.mark.asyncio
async def test_broker_depends(broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    @use_context
    async def depends(body, message):
        return message

    check_message = None
    async def consumer(body, message, k = Depends(depends)):
        nonlocal check_message
        check_message = message is k

    broker.handle("test_broker_depends")(consumer)
    
    await broker.start()
    await broker.publish_message(message="hello", queue="test_broker_depends")

    tries = 0
    while tries < 20:
        await asyncio.sleep(0.1)
        if check_message is not None:
            break
        else:
            tries += 1
    
    assert check_message
