from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

from fastapi import APIRouter, params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable
from fastapi.utils import generate_unique_id
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
from typing_extensions import ClassVar

from propan.brokers._model import BrokerUsecase
from propan.fastapi.core.route import PropanRoute
from propan.types import AnyDict


class PropanRouter(APIRouter):
    broker_class: ClassVar[Type[BrokerUsecase]]
    broker: BrokerUsecase

    @property
    def mq_routes(self) -> Tuple[PropanRoute, ...]:
        return tuple(
            filter(lambda x: isinstance(x, PropanRoute), self.routes)  # type: ignore
        )

    async def _connect(self) -> None:
        await self.broker.start()

    async def _close(self) -> None:
        await self.broker.close()

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
        generate_unique_id_function: Callable[[APIRoute], str] = Default(
            generate_unique_id
        ),
        **connection_kwars: AnyDict,
    ) -> None:
        assert (
            self.broker_class
        ), "You should specify `broker_class` at your implementation"

        self.broker = self.broker_class(
            *connection_args,
            **{**connection_kwars, "apply_types": False},  # type: ignore
        )

        on_startup = [] if on_startup is None else list(on_startup)
        on_shutdown = [] if on_shutdown is None else list(on_shutdown)
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
            on_startup=[self._connect] + on_startup,
            on_shutdown=on_shutdown + [self._close],
        )

    def add_api_mq_route(
        self,
        path: str,
        *,
        endpoint: Callable[..., Any],
        **broker_kwargs: AnyDict,
    ) -> None:
        route = PropanRoute(
            path,
            endpoint=endpoint,
            dependency_overrides_provider=self.dependency_overrides_provider,
            broker=self.broker,
            **broker_kwargs,
        )
        self.routes.append(route)

    def event(
        self,
        path: str,
        **broker_kwargs: Dict[str, Any],
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_mq_route(
                path,
                endpoint=func,
                **broker_kwargs,
            )
            return func

        return decorator
