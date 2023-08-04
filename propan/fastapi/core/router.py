import json
from contextlib import asynccontextmanager
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from fastapi import APIRouter, FastAPI, Request, params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette import routing
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import _DefaultLifespan
from starlette.types import AppType, ASGIApp, Lifespan
from typing_extensions import TypeVar

from propan.brokers._model.broker_usecase import (
    BrokerAsyncUsecase,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import Queue
from propan.cli.docs.gen import (
    gen_app_schema_json,
    gen_app_schema_yaml,
    get_app_schema,
    json_schema_to_yaml,
    schema_to_json,
)
from propan.cli.docs.serving import get_asyncapi_html
from propan.fastapi.core.route import PropanRoute
from propan.types import AnyDict
from propan.utils.functions import to_async

Broker = TypeVar("Broker", bound=BrokerAsyncUsecase[Any, Any])
MsgType = TypeVar("MsgType")


class PropanRouter(APIRouter, Generic[Broker, MsgType]):
    broker_class: Type[Broker]
    broker: Broker
    docs_router: Optional[APIRouter]
    _after_startup_hooks: List[
        Callable[[AppType], Awaitable[Optional[Mapping[str, Any]]]]
    ]

    def __init__(
        self,
        *connection_args: Tuple[Any, ...],
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[routing.BaseRoute]] = None,
        routes: Optional[List[routing.BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[APIRoute] = APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        schema_url: str = "/asyncapi",
        lifespan: Optional[Lifespan[Any]] = None,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(
            generate_unique_id
        ),
        setup_state: bool = True,
        **connection_kwars: AnyDict,
    ) -> None:
        assert (
            self.broker_class
        ), "You should specify `broker_class` at your implementation"

        self.broker = self.broker_class(
            *connection_args,
            apply_types=False,
            **connection_kwars,  # type: ignore
        )
        self.setup_state = setup_state

        super().__init__(
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default,
            dependency_overrides_provider=dependency_overrides_provider,
            route_class=route_class,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function,
            lifespan=self.wrap_lifespan(lifespan),
            on_startup=on_startup,
            on_shutdown=on_shutdown,
        )

        if self.include_in_schema is True:  # pragma: no branch
            docs_router = APIRouter(
                prefix=prefix,
                tags=["asyncapi"],
                redirect_slashes=redirect_slashes,
                default=default,
                deprecated=deprecated,
            )
            docs_router.get(schema_url)(serve_asyncapi_schema)
            docs_router.get(f"{schema_url}.json")(download_app_json_schema)
            docs_router.get(f"{schema_url}.yaml")(download_app_yaml_schema)
            self.docs_router = docs_router
        else:
            self.docs_router = None

        self._after_startup_hooks = []

    def add_api_mq_route(
        self,
        path: Union[Queue, str],
        *extra: Union[Queue, str],
        endpoint: HandlerCallable[T_HandlerReturn],
        dependencies: Sequence[params.Depends],
        **broker_kwargs: AnyDict,
    ) -> Callable[[Any, bool], Awaitable[T_HandlerReturn]]:
        route = PropanRoute(
            path,
            *extra,
            endpoint=endpoint,
            dependencies=dependencies,
            dependency_overrides_provider=self.dependency_overrides_provider,
            broker=self.broker,
            **broker_kwargs,
        )
        self.routes.append(route)
        return route.handler

    def event(
        self,
        path: Union[str, Queue],
        *extra: Union[Queue, str],
        dependencies: Optional[Sequence[params.Depends]] = None,
        **broker_kwargs: Dict[str, Any],
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[MsgType, bool], Awaitable[T_HandlerReturn]],
    ]:
        current_dependencies = self.dependencies.copy()
        if dependencies:
            current_dependencies.extend(dependencies)

        def decorator(
            func: HandlerCallable[T_HandlerReturn],
        ) -> Callable[[MsgType, bool], Awaitable[T_HandlerReturn]]:
            return self.add_api_mq_route(
                path,
                *extra,
                endpoint=func,
                dependencies=current_dependencies,
                **broker_kwargs,
            )

        return decorator

    def wrap_lifespan(self, lifespan: Optional[Lifespan[Any]] = None) -> Lifespan[Any]:
        if lifespan is not None:
            lifespan_context = lifespan
        else:
            lifespan_context = _DefaultLifespan(self)

        @asynccontextmanager
        async def start_broker_lifespan(
            app: FastAPI,
        ) -> AsyncIterator[Mapping[str, Any]]:
            app.broker = self.broker  # type: ignore
            if self.docs_router:
                app.include_router(self.docs_router)

            async with lifespan_context(app) as maybe_context:
                if maybe_context is None:
                    context: Dict[str, Any] = {}
                else:
                    context = dict(maybe_context)

                context.update({"broker": self.broker})

                await self.broker.start()

                for h in self._after_startup_hooks:
                    h_context = await h(app)
                    if h_context:  # pragma: no branch
                        context.update(h_context)

                if self.setup_state:
                    yield context
                else:
                    yield

                await self.broker.close()

        return start_broker_lifespan

    def after_startup(
        self,
        func: Union[
            Callable[[AppType], Mapping[str, Any]],
            Callable[[AppType], Awaitable[Mapping[str, Any]]],
            Callable[[AppType], None],
            Callable[[AppType], Awaitable[None]],
        ],
    ) -> None:
        self._after_startup_hooks.append(to_async(func))  # type: ignore


def download_app_json_schema(r: Request) -> Response:
    return Response(
        content=json.dumps(
            gen_app_schema_json(r.app),
            indent=4,
        ),
        headers={
            "Content-Type": "application/octet-stream",
        },
    )


def download_app_yaml_schema(r: Request) -> Response:
    return Response(
        content=gen_app_schema_yaml(r.app),
        headers={
            "Content-Type": "application/octet-stream",
        },
    )


def serve_asyncapi_schema(
    r: Request,
    sidebar: bool = True,
    info: bool = True,
    servers: bool = True,
    operations: bool = True,
    messages: bool = True,
    schemas: bool = True,
    errors: bool = True,
    expandMessageExamples: bool = True,
) -> HTMLResponse:
    raw_schema = get_app_schema(r.app)
    json_schema = schema_to_json(raw_schema)
    schema = json_schema_to_yaml(json_schema)
    return HTMLResponse(
        content=get_asyncapi_html(
            schema,
            sidebar=sidebar,
            info=info,
            servers=servers,
            operations=operations,
            messages=messages,
            schemas=schemas,
            errors=errors,
            expand_message_examples=expandMessageExamples,
            title=raw_schema.info.title if raw_schema else "Propan",
        )
    )
