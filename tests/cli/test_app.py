import logging
import os
import signal
from unittest.mock import Mock, patch

import anyio
import pytest

from propan import PropanApp
from propan.log import logger
from propan.rabbit import RabbitBroker
from propan.utils import Context
from tests.tools.marks import needs_py38


def test_init(app: PropanApp, context: Context, broker: RabbitBroker):
    assert app.broker is broker
    assert context.app is app
    assert app.logger is logger


def test_init_without_broker(app_without_broker: PropanApp):
    assert app_without_broker.broker is None


def test_init_without_logger(app_without_logger: PropanApp):
    assert app_without_logger.logger is None


def test_set_broker(broker: RabbitBroker, app_without_broker: PropanApp):
    assert app_without_broker.broker is None
    app_without_broker.set_broker(broker)
    assert app_without_broker.broker is broker


def test_log(app: PropanApp, app_without_logger: PropanApp):
    app._log(logging.INFO, "test")
    app_without_logger._log(logging.INFO, "test")


@pytest.mark.asyncio
async def test_startup_calls_lifespans(mock: Mock, app_without_broker: PropanApp):
    def call1():
        mock.call_start1()
        assert not mock.call_start2.called

    def call2():
        mock.call_start2()
        assert mock.call_start1.call_count == 1

    app_without_broker.on_startup(call1)
    app_without_broker.on_startup(call2)

    await app_without_broker._startup()

    mock.call_start1.assert_called_once()
    mock.call_start2.assert_called_once()


@pytest.mark.asyncio
async def test_shutdown_calls_lifespans(mock: Mock, app_without_broker: PropanApp):
    def call1():
        mock.call_stop1()
        assert not mock.call_stop2.called

    def call2():
        mock.call_stop2()
        assert mock.call_stop1.call_count == 1

    app_without_broker.on_shutdown(call1)
    app_without_broker.on_shutdown(call2)

    await app_without_broker._shutdown()

    mock.call_stop1.assert_called_once()
    mock.call_stop2.assert_called_once()


@pytest.mark.asyncio
@needs_py38
async def test_startup_lifespan_before_broker_started(async_mock, app: PropanApp):
    @app.on_startup
    async def call():
        await async_mock.before()
        assert not async_mock.broker_start.called

    @app.after_startup
    async def call_after():
        await async_mock.after()
        async_mock.before.assert_awaited_once()
        async_mock.broker_start.assert_called_once()

    with patch.object(app.broker, "start", async_mock.broker_start):
        await app._startup()

    async_mock.broker_start.assert_called_once()
    async_mock.after.assert_awaited_once()
    async_mock.before.assert_awaited_once()


@pytest.mark.asyncio
@needs_py38
async def test_shutdown_lifespan_after_broker_stopped(mock, async_mock, app: PropanApp):
    @app.after_shutdown
    async def call():
        await async_mock.after()
        async_mock.broker_stop.assert_called_once()

    @app.on_shutdown
    async def call_before():
        await async_mock.before()
        assert not async_mock.broker_stop.called

    with patch.object(app.broker, "close", async_mock.broker_stop):
        await app._shutdown()

    async_mock.broker_stop.assert_called_once()
    async_mock.after.assert_awaited_once()
    async_mock.before.assert_awaited_once()


@pytest.mark.asyncio
@needs_py38
async def test_running(async_mock, app: PropanApp):
    app._init_async_cycle()
    app._stop_event.set()

    with patch.object(app.broker, "start", async_mock.broker_run):
        with patch.object(app.broker, "close", async_mock.broker_stopped):
            await app.run()

    async_mock.broker_run.assert_called_once()
    async_mock.broker_stopped.assert_called_once()


@pytest.mark.asyncio
@needs_py38
async def test_stop_with_sigint(async_mock, app: PropanApp):
    app._init_async_cycle()

    with patch.object(app.broker, "start", async_mock.broker_run_sigint):
        with patch.object(app.broker, "close", async_mock.broker_stopped_sigint):
            async with anyio.create_task_group() as tg:
                tg.start_soon(app.run)
                tg.start_soon(_kill, signal.SIGINT)

    async_mock.broker_run_sigint.assert_called_once()
    async_mock.broker_stopped_sigint.assert_called_once()


@pytest.mark.asyncio
@needs_py38
async def test_stop_with_sigterm(async_mock, app: PropanApp):
    app._init_async_cycle()

    with patch.object(app.broker, "start", async_mock.broker_run_sigterm):
        with patch.object(app.broker, "close", async_mock.broker_stopped_sigterm):
            async with anyio.create_task_group() as tg:
                tg.start_soon(app.run)
                tg.start_soon(_kill, signal.SIGTERM)

    async_mock.broker_run_sigterm.assert_called_once()
    async_mock.broker_stopped_sigterm.assert_called_once()


async def _kill(sig):
    os.kill(os.getpid(), sig)
