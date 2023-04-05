import pytest

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
        pass
    
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
