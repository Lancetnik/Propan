import pytest
from typing_extensions import Annotated

from propan.utils import Depends, apply_types


def sync_dep(key):
    return key


async def async_dep(key):
    return key


@pytest.mark.asyncio
async def test_sync_depends():
    key = 1000

    @apply_types
    def func(k=Depends(sync_dep)):
        return k is key

    assert func(key=key)


@pytest.mark.asyncio
async def test_sync_with_async_depends():
    with pytest.raises(AssertionError):

        @apply_types
        def func(k=Depends(async_dep)):  # pragma: no cover
            pass


@pytest.mark.asyncio
async def test_async_depends():
    key = 1000

    @apply_types
    async def func(k=Depends(async_dep)):
        return k is key

    assert await func(key=key)


@pytest.mark.asyncio
async def test_async_with_sync_depends():
    key = 1000

    @apply_types
    async def func(k=Depends(sync_dep)):
        return k is key

    assert await func(key=key)


@pytest.mark.asyncio
async def test_annotated_depends():
    D = Annotated[int, Depends(sync_dep)]

    key = 1000

    @apply_types
    async def func(k: D):
        return k == key

    assert await func(key=key)
