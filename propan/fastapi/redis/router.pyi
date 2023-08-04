import logging
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    Union,
)

from fastapi import params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from redis.asyncio.connection import BaseParser, DefaultParser, Encoder
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from propan import RedisBroker
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.fastapi.core.router import PropanRouter
from propan.log import access_logger
from propan.types import AnyDict

class RedisRouter(PropanRouter[RedisBroker]):
    def __init__(
        self,
        url: str = "redis://localhost:6379",
        polling_interval: float = 1.0,
        host: str = "localhost",
        port: Union[str, int] = 6379,
        db: Union[str, int] = 0,
        password: Optional[str] = None,
        socket_timeout: Optional[float] = None,
        socket_connect_timeout: Optional[float] = None,
        socket_keepalive: bool = False,
        socket_keepalive_options: Optional[Mapping[int, Union[int, bytes]]] = None,
        socket_type: int = 0,
        retry_on_timeout: bool = False,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        parser_class: Type[BaseParser] = DefaultParser,
        socket_read_size: int = 65536,
        health_check_interval: float = 0,
        client_name: Optional[str] = None,
        username: Optional[str] = None,
        encoder_class: Type[Encoder] = Encoder,
        # FastAPI kwargs
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
        # Broker kwargs
        schema_url: str = "/asyncapi",
        setup_state: bool = True,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        protocol: str = "redis",
    ) -> None:
        pass
    def add_api_mq_route(  # type: ignore[override]
        self,
        channel: str,
        *,
        endpoint: HandlerCallable[T_HandlerReturn],
        pattern: bool = False,
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        description: str = "",
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]]:
        pass
    def event(  # type: ignore[override]
        self,
        channel: str,
        *,
        pattern: bool = False,
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        description: str = "",
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]:
        pass
