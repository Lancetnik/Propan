import logging
from enum import Enum
from ssl import SSLContext
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Type, Union

import aio_pika
from aio_pika.message import IncomingMessage
from fastapi import params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from pamqp.common import FieldTable
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from propan import RabbitBroker
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
from propan.fastapi.core import PropanRouter
from propan.log import access_logger
from propan.types import AnyDict

class RabbitRouter(PropanRouter[RabbitBroker]):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
        ssl: bool = False,
        ssl_options: Optional[aio_pika.abc.SSLOptions] = None,
        ssl_context: Optional[SSLContext] = None,
        timeout: aio_pika.abc.TimeoutType = None,
        client_properties: Optional[FieldTable] = None,
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
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        consumers: Optional[int] = None,
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        schema_url: str = "/asyncapi",
        setup_state: bool = True,
        protocol: str = "amqp",
        protocol_version: str = "0.9.1",
    ) -> None:
        pass
    def add_api_mq_route(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        *,
        endpoint: HandlerCallable[T_HandlerReturn],
        exchange: Union[str, RabbitExchange, None] = None,
        retry: Union[bool, int] = False,
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        description: str = "",
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> Callable[[IncomingMessage, bool], Awaitable[T_HandlerReturn]]:
        pass
    def event(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        *,
        exchange: Union[str, RabbitExchange, None] = None,
        consume_arguments: Optional[AnyDict] = None,
        retry: Union[bool, int] = False,
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        description: str = "",
        dependencies: Optional[Sequence[params.Depends]] = None,
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[IncomingMessage, bool], Awaitable[T_HandlerReturn]],
    ]:
        pass
