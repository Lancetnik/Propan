from unittest.mock import Mock

import pytest
from fastapi import FastAPI

from propan.fastapi import RabbitRouter
from propan.test.rabbit import TestRabbitBroker, build_message
from tests.fastapi.case import FastAPITestcase


class TestRabbitRouter(FastAPITestcase):
    router_class = RabbitRouter
    broker_test = staticmethod(TestRabbitBroker)
    build_message = staticmethod(build_message)

    @pytest.mark.asyncio
    async def test_after_startup(self, mock: Mock):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        app = FastAPI()
        app.include_router(router)

        @router.after_startup
        def test_sync(app):
            mock.sync_called()
            return {"sync_called": mock.async_called.called is False}

        @router.after_startup
        async def test_async(app):
            mock.async_called()
            return {"async_called": mock.sync_called.called}

        async with router.lifespan_context(app) as context:
            assert context["sync_called"]
            assert context["async_called"]

        mock.sync_called.assert_called_once()
        mock.async_called.assert_called_once()
