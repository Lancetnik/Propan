import asyncio

import pytest

from propan.brokers import RabbitBroker
from propan.utils.context import Depends, use_context


def sync_dep(key):
    return key

async def async_dep(key):
    return key


@pytest.mark.asyncio
async def test_sync_depends():
    key = 1000

    @use_context
    def func(*args, k = Depends(sync_dep), **kwargs):
        return k is key
    
    assert func(key=key)


@pytest.mark.asyncio
async def test_sync_with_async_depends():
    key = 1000

    @use_context
    def func(*args, k = Depends(async_dep), **kwargs):
        return k is key
    
    with pytest.raises(ValueError):
        func(key=key)


@pytest.mark.asyncio
async def test_async_depends():
    key = 1000

    @use_context
    async def func(*args, k = Depends(async_dep), **kwargs):
        return k is key
    
    assert await func(key=key)


@pytest.mark.asyncio
async def test_async_with_sync_depends():
    key = 1000

    @use_context
    async def func(*args, k = Depends(sync_dep), **kwargs):
        return k is key
    
    assert await func(key=key)


@pytest.mark.asyncio
async def test_broker_depends(broker: RabbitBroker):
    await broker.connect()
    await broker.init_channel()

    @use_context
    def sync_depends(body, message):
        return message

    @use_context
    async def async_depends(body, message):
        return message

    check_message = None
    async def consumer(body, message, k1 = Depends(sync_depends), k2 = Depends(async_depends)):
        nonlocal check_message
        check_message = message is k1 is k2

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
