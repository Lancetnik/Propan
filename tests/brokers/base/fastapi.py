import asyncio
from contextlib import asynccontextmanager
from typing import Callable, Type, TypeVar
from unittest.mock import Mock

import pytest
from fastapi import Depends, FastAPI, Header
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.fastapi.router import PropanRouter
from propan.types import AnyCallable

Broker = TypeVar("Broker", bound=BrokerAsyncUsecase)


@pytest.mark.asyncio
class FastAPITestcase:
    router_class: Type[PropanRouter[BrokerAsyncUsecase]]

    async def test_base_real(self, mock: Mock, queue: str, event: asyncio.Event):
        router = self.router_class()

        @router.subscriber(queue)
        async def hello(msg):
            event.set()
            return mock(msg)

        async with router.broker:
            await router.broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(router.broker.publish("hi", queue)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_with("hi")

    async def test_double_real(self, mock: Mock, queue: str, event: asyncio.Event):
        event2 = asyncio.Event()
        router = self.router_class()

        @router.subscriber(queue)
        @router.subscriber(queue + "2")
        async def hello(msg):
            if event.is_set():
                event2.set()
            else:
                event.set()
            mock()

        async with router.broker:
            await router.broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(router.broker.publish("hi", queue)),
                    asyncio.create_task(router.broker.publish("hi", queue + "2")),
                    asyncio.create_task(event.wait()),
                    asyncio.create_task(event2.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        assert event2.is_set()
        assert mock.call_count == 2

    async def test_base_publisher_real(
        self, mock: Mock, queue: str, event: asyncio.Event
    ):
        router = self.router_class()

        @router.subscriber(queue)
        @router.publisher(queue + "resp")
        async def m():
            return "hi"

        @router.subscriber(queue + "resp")
        async def resp(msg):
            event.set()
            mock(msg)

        async with router.broker:
            await router.broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(router.broker.publish("", queue)),
                    asyncio.create_task(event.wait()),
                ),
                timeout=3,
            )

        assert event.is_set()
        mock.assert_called_once_with("hi")


@pytest.mark.asyncio
class FastAPILocalTestcase:
    router_class: Type[PropanRouter[BrokerAsyncUsecase]]
    broker_test: Callable[[Broker], Broker]
    build_message: AnyCallable

    async def test_base(self, queue: str):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        app = FastAPI(lifespan=router.lifespan_context)

        @router.subscriber(queue)
        async def hello():
            return "hi"

        async with router.broker:
            with TestClient(app) as client:
                assert client.app_state["broker"] is router.broker

                r = await router.broker.publish("hi", queue, rpc=True, rpc_timeout=0.5)
                assert r == "hi"

    async def test_invalid(self, queue: str):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        app = FastAPI(lifespan=router.lifespan_context)

        @router.subscriber(queue)
        async def hello(msg: int):  # pragma: no cover
            return msg

        app.include_router(router)

        async with router.broker:
            with TestClient(app):
                with pytest.raises(RequestValidationError):
                    await router.broker.publish("hi", queue)

    async def test_headers(self, queue: str):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        @router.subscriber(queue)
        async def hello(w=Header()):
            return w

        async with router.broker:
            r = await router.broker.publish(
                "", queue, headers={"w": "hi"}, rpc=True, rpc_timeout=0.5
            )
            assert r == "hi"

    async def test_depends(self, mock: Mock, queue: str):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        def dep(a):
            mock(a)
            return a

        @router.subscriber(queue)
        async def hello(a, w=Depends(dep)):
            return w

        async with router.broker:
            r = await router.broker.publish(
                {"a": "hi"}, queue, rpc=True, rpc_timeout=0.5
            )
            assert r == "hi"

        mock.assert_called_once_with("hi")

    async def test_yield_depends(self, mock: Mock, queue: str):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        def dep(a):
            mock.start()
            yield a
            mock.close()

        @router.subscriber(queue)
        async def hello(a, w=Depends(dep)):
            mock.start.assert_called_once()
            assert not mock.close.call_count
            return w

        async with router.broker:
            r = await router.broker.publish(
                {"a": "hi"}, queue, rpc=True, rpc_timeout=0.5
            )
            assert r == "hi"

        mock.start.assert_called_once()
        mock.close.assert_called_once()

    async def test_router_depends(self, mock: Mock, queue: str):
        def mock_dep():
            mock()

        router = self.router_class(dependencies=(Depends(mock_dep, use_cache=False),))
        router.broker = self.broker_test(router.broker)

        @router.subscriber(queue)
        async def hello(a):
            return a

        async with router.broker:
            r = await router.broker.publish("hi", queue, rpc=True, rpc_timeout=0.5)
            assert r == "hi"

        mock.assert_called_once()

    async def test_subscriber_depends(self, mock: Mock, queue: str):
        def mock_dep():
            mock()

        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        @router.subscriber(queue, dependencies=(Depends(mock_dep, use_cache=False),))
        async def hello(a):
            return a

        async with router.broker:
            r = await router.broker.publish("hi", queue, rpc=True, rpc_timeout=0.5)
            assert r == "hi"

        mock.assert_called_once()

    async def test_after_startup(self, mock: Mock):
        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        app = FastAPI(lifespan=router.lifespan_context)
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

    async def test_existed_lifespan_startup(self, mock: Mock):
        @asynccontextmanager
        async def lifespan(app):
            mock.start()
            yield {"lifespan": True}
            mock.close()

        router = self.router_class(lifespan=lifespan)
        router.broker = self.broker_test(router.broker)

        app = FastAPI(lifespan=router.lifespan_context)
        app.include_router(router)

        async with router.lifespan_context(app) as context:
            assert context["lifespan"]

        mock.start.assert_called_once()
        mock.close.assert_called_once()

    async def test_subscriber_mock(self, queue: str):
        router = self.router_class()

        @router.subscriber(queue)
        async def m():
            return "hi"

        async with self.broker_test(router.broker) as rb:
            await rb.publish("hello", queue)
            m.mock.assert_called_once_with("hello")

    async def test_publisher_mock(self, queue: str):
        router = self.router_class()

        publisher = router.publisher(queue + "resp")

        @publisher
        @router.subscriber(queue)
        async def m():
            return "response"

        async with self.broker_test(router.broker) as rb:
            await rb.publish("hello", queue)
            publisher.mock.assert_called_with("response")
