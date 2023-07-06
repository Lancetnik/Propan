import asyncio
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Optional, Tuple, Type
from unittest.mock import Mock

import pytest

from propan import BaseMiddleware
from propan.brokers._model.broker_usecase import BrokerAsyncUsecase
from propan.types import AnyCallable


def get_middleware_class() -> Tuple[Type[BaseMiddleware], Mock]:
    mock = Mock()

    class MockMiddleware(BaseMiddleware):
        def __init__(self, message):
            super().__init__(message)
            self.mock = mock

        async def __aenter__(self):
            self.mock.enter()
            return await super().__aenter__()

        async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]] = None,
            exc_val: Optional[BaseException] = None,
            exec_tb: Optional[TracebackType] = None,
        ):
            self.mock.exit()
            return await super().__aexit__(exc_type, exc_val, exec_tb)

    return MockMiddleware, mock


def get_middleware_function():
    mock = Mock()

    @asynccontextmanager
    async def middleware(message):
        mock.enter()
        yield
        mock.exit()

    return middleware, mock


class MiddlewareTestCase:
    build_message: AnyCallable

    @staticmethod
    @pytest.fixture(params=[get_middleware_class, get_middleware_function])
    def get_middleware(request):
        return request.param()

    @staticmethod
    @pytest.mark.asyncio
    async def test_base(get_middleware, queue: str, broker: BrokerAsyncUsecase):
        middleware, mock = get_middleware

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        broker.include_middleware(middleware)

        @broker.handle(queue)
        async def handler(m):
            mock(m)
            mock.enter.assert_called_once()
            assert not mock.exit.called
            return m

        async with broker:
            await broker.start()
            await broker.publish("test", queue)
            await asyncio.wait_for(consume.wait(), 3)

        mock.assert_called_with("test")
        mock.enter.assert_called_once()
        mock.exit.assert_called_once()

    @staticmethod
    @pytest.mark.asyncio
    async def test_with_test(
        get_middleware, queue: str, test_broker: BrokerAsyncUsecase
    ):
        middleware, mock = get_middleware
        test_broker.include_middleware(middleware)

        @test_broker.handle(queue)
        async def handler(m):
            mock.enter.assert_called_once()
            assert not mock.exit.called
            return m

        await test_broker.publish("test", queue, callback=True)
        mock.enter.assert_called_once()
        mock.exit.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_build(
        self, get_middleware, queue: str, test_broker: BrokerAsyncUsecase
    ):
        middleware, mock = get_middleware
        test_broker.include_middleware(middleware)

        @test_broker.handle(queue)
        async def handler(m):
            mock.enter.assert_called_once()
            assert not mock.exit.called
            return m

        message = self.build_message("test", queue)
        await handler(message, True)

        mock.enter.assert_called_once()
        mock.exit.assert_called_once()
