from typing import Callable, Type, TypeVar
from uuid import uuid4

import pytest
from fastapi import APIRouter, FastAPI

Broker = TypeVar("Broker")


class FastAPITestcase:
    router_class: Type[APIRouter]
    broker_test: Callable[[Broker], Broker]

    @pytest.mark.asyncio
    async def test(self):
        name = str(uuid4())
        name2 = name + "1"

        router = self.router_class()
        router.broker = self.broker_test(router.broker)

        app = FastAPI()
        app.include_router(router)

        @router.event(name)
        async def hello():
            return "1"

        @router.event(name2)
        async def hello2(b: int):
            return "2"

        async with router.lifespan_context(None):
            r = await router.broker.publish(
                "", name, callback=True, callback_timeout=0.5
            )
            assert r == "1"

            r = await router.broker.publish(
                "2", name2, callback=True, callback_timeout=0.5
            )
            assert r == "2"
