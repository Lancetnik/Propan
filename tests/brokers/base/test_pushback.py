from unittest.mock import AsyncMock

import pytest
from propan.brokers.push_back_watcher import (
    FakePushBackWatcher,
    PushBackWatcher,
    WatcherContext,
)


@pytest.mark.asyncio
async def test_push_back_correct(async_mock: AsyncMock):
    message_id = 1

    watcher = PushBackWatcher(3)

    context = WatcherContext(
        watcher,
        message_id,
        on_success=async_mock.on_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async with context:
        await async_mock()

    async_mock.on_success.assert_awaited_once()
    assert not watcher.memory.get(message_id)


@pytest.mark.asyncio
async def test_push_back_endless_correct(async_mock: AsyncMock):
    message_id = 1

    watcher = FakePushBackWatcher()

    context = WatcherContext(
        watcher,
        message_id,
        on_success=async_mock.on_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async with context:
        await async_mock()

    async_mock.on_success.assert_awaited_once()


@pytest.mark.asyncio
async def test_push_back_watcher(async_mock: AsyncMock):
    watcher = PushBackWatcher(3)

    context = WatcherContext(
        watcher,
        1,
        on_success=async_mock.on_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async_mock.side_effect = Exception("Ooops!")

    while not async_mock.on_max.called:
        with pytest.raises(Exception):
            async with context:
                await async_mock()

    assert not async_mock.on_success.called
    assert async_mock.on_error.call_count == 3
    async_mock.on_max.assert_awaited_once()


@pytest.mark.asyncio
async def test_push_endless_back_watcher(async_mock: AsyncMock):
    watcher = FakePushBackWatcher()

    context = WatcherContext(
        watcher,
        1,
        on_success=async_mock.on_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async_mock.side_effect = Exception("Ooops!")

    while async_mock.on_error.call_count < 10:
        with pytest.raises(Exception):
            async with context:
                await async_mock()

    assert not async_mock.on_success.called
    assert not async_mock.on_max.called
    assert async_mock.on_error.call_count == 10
