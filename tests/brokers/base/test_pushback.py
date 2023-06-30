from unittest.mock import MagicMock

import pytest

from propan.brokers.exceptions import SkipMessage
from propan.brokers.push_back_watcher import (
    FakePushBackWatcher,
    PushBackWatcher,
    WatcherContext,
)
from tests.tools.marks import needs_py38


@pytest.fixture
def message():
    return MagicMock(message_id=1)


@pytest.mark.asyncio
@needs_py38
async def test_push_back_correct(async_mock, message):
    async def call_success(m):
        assert m.message_id == 1
        await async_mock.on_success()

    watcher = PushBackWatcher(3)

    context = WatcherContext(
        watcher,
        message,
        on_success=call_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async with context:
        await async_mock()

    async_mock.on_success.assert_awaited_once()
    assert not watcher.memory.get(message.message_id)


@pytest.mark.asyncio
@needs_py38
async def test_push_back_endless_correct(async_mock, message):
    async def call_success(m):
        assert m.message_id == 1
        await async_mock.on_success()

    watcher = FakePushBackWatcher()

    context = WatcherContext(
        watcher,
        message,
        on_success=call_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async with context:
        await async_mock()

    async_mock.on_success.assert_awaited_once()


@pytest.mark.asyncio
@needs_py38
async def test_push_back_watcher(async_mock, message):
    async def call_error(m):
        assert m.message_id == 1
        await async_mock.on_error()

    async def call_max(m):
        assert m.message_id == 1
        await async_mock.on_max()

    watcher = PushBackWatcher(3)

    context = WatcherContext(
        watcher,
        message,
        on_success=async_mock.on_success,
        on_error=call_error,
        on_max=call_max,
    )

    async_mock.side_effect = ValueError("Ooops!")

    while not async_mock.on_max.called:
        with pytest.raises(ValueError):
            async with context:
                await async_mock()

    assert not async_mock.on_success.called
    assert async_mock.on_error.await_count == 3
    async_mock.on_max.assert_awaited_once()


@pytest.mark.asyncio
@needs_py38
async def test_push_endless_back_watcher(async_mock, message):
    async def call_error(m):
        assert m.message_id == 1
        await async_mock.on_error()

    watcher = FakePushBackWatcher()

    context = WatcherContext(
        watcher,
        message,
        on_success=async_mock.on_success,
        on_error=call_error,
        on_max=async_mock.on_max,
    )

    async_mock.side_effect = ValueError("Ooops!")

    while async_mock.on_error.await_count < 10:
        with pytest.raises(ValueError):
            async with context:
                await async_mock()

    assert not async_mock.on_success.called
    assert not async_mock.on_max.called
    assert async_mock.on_error.await_count == 10


@pytest.mark.asyncio
@needs_py38
async def test_ignore_skip(async_mock, message):
    watcher = PushBackWatcher(3)

    context = WatcherContext(
        watcher,
        message,
        on_success=async_mock.on_success,
        on_error=async_mock.on_error,
        on_max=async_mock.on_max,
    )

    async_mock.side_effect = SkipMessage()

    with pytest.raises(SkipMessage):
        async with context:
            await async_mock()

    assert not async_mock.on_error.called
    assert not async_mock.on_max.called
    assert not async_mock.on_success.called
