from typing import Callable, Type, TypeVar
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import APIRouter, Depends, FastAPI, Header
from fastapi.testclient import TestClient


Broker = TypeVar("Broker")


class FastAPITestcase:
    router_class: Type[APIRouter]
    broker_test: Callable[[Broker], Broker]

    @pytest.mark.asyncio
    async def test(self, mock: Mock):
        name = str(uuid4())
        name2 = name + "1"
        name3 = name + "2"

        def mock_dep():
            mock.dep()

        router = self.router_class(dependencies=(Depends(mock_dep, use_cache=False),))
        router.broker = self.broker_test(router.broker)

        app = FastAPI(lifespan=router.lifespan_context)
        app.include_router(router)

        def dep(a: str, c: str):
            mock(f"{a}, {c}")

        @router.event(name)
        async def hello():
            return "1"

        @router.event(name2)
        async def hello2(b: int, w=Header()):  # noqa: B008
            return w

        @router.event(name3, dependencies=(Depends(mock_dep, use_cache=False),))
        async def hello3(a: str, b: int, d=Depends(dep)):
            return "3"

        with TestClient(app) as client:
            assert client.app_state["broker"] is router.broker

            r = await router.broker.publish(
                "", name, callback=True, callback_timeout=0.5
            )
            assert r == "1"

            r = await router.broker.publish(
                "2", name2, headers={"w": "2"}, callback=True, callback_timeout=0.5
            )
            assert r == "2"

            r = await router.broker.publish(
                {
                    "a": "hi",
                    "b": 1,
                    "c": "depends",
                },
                name3,
                callback=True,
                callback_timeout=0.5,
            )
            assert r == "3"

        mock.assert_called_with("hi, depends")
        assert mock.dep.call_count == 4
