from contextlib import asynccontextmanager
from unittest.mock import Mock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from propan._compat import ResponseValidationError
from propan.fastapi import KafkaRouter
from propan.test import TestKafkaBroker
from propan.test.kafka import build_message
from tests.tools.marks import needs_py38


@pytest.fixture()
def router():
    router = KafkaRouter(schema_url="/schema")
    router.broker = TestKafkaBroker(router.broker)
    return router


@needs_py38
def test_nested_lifespan(mock: Mock):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mock.started()
        yield {"lifespan": True}
        mock.closed()

    router = KafkaRouter(lifespan=lifespan)
    router.broker = TestKafkaBroker(router.broker)

    app = FastAPI(lifespan=router.lifespan_context)
    app.include_router(router)

    with TestClient(app) as client:
        mock.started.assert_called_once()
        router.broker.start.assert_called_once()
        assert client.app_state["lifespan"] is True
        assert client.app_state["broker"] is router.broker

    mock.closed.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_request(router: KafkaRouter):
    @router.event("test")
    async def handler(a: int, b: str):
        ...

    msg = build_message("Hello", "test")

    with pytest.raises(ResponseValidationError):
        await handler(msg, reraise_exc=True)


def test_get_schema_yaml(router: KafkaRouter):
    app = FastAPI(lifespan=router.lifespan_context)
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/schema.yaml")

    assert response.status_code == 200


def test_get_schema_json():
    async def dep3(k: str):
        ...

    async def dep2(m: str):
        ...

    router = KafkaRouter(dependencies=(Depends(dep3),))
    router.broker = TestKafkaBroker(router.broker)

    async def dep(a: str, c: float):
        ...

    @router.event("test", dependencies=(Depends(dep2),))
    async def handler(a: str, b: int, d=Depends(dep)):
        ...

    app = FastAPI(lifespan=router.lifespan_context)
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/asyncapi.json")

    assert response.status_code == 200

    assert set(
        response.json()["components"]["schemas"]["HandlerPayload"]["properties"].keys()
    ) == {"a", "b", "c", "m", "k"}


def test_get_schema_html(router: KafkaRouter):
    app = FastAPI(lifespan=router.lifespan_context)
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/schema")

    assert response.status_code == 200


def test_not_generate_schema(router: KafkaRouter):
    router = KafkaRouter(include_in_schema=False)
    router.broker = TestKafkaBroker(router.broker)
    app = FastAPI(lifespan=router.lifespan_context)
    app.include_router(router)

    with TestClient(app) as client:
        response = client.get("/schema")

    assert response.status_code == 404
