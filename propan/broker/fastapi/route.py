import asyncio
import inspect
from contextlib import AsyncExitStack
from functools import wraps
from itertools import dropwhile
from typing import Any, Callable, Coroutine, Optional, Sequence, Union

from fastapi import params
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import (
    get_dependant,
    get_parameterless_sub_dependant,
    solve_dependencies,
)
from fastapi.routing import run_endpoint_function
from starlette.requests import Request
from starlette.routing import BaseRoute

from propan._compat import raise_fastapi_validation_error
from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.message import PropanMessage as NativeMessage
from propan.broker.schemas import NameRequired
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.broker.wrapper import HandlerCallWrapper
from propan.types import AnyDict


class PropanRoute(BaseRoute):
    def __init__(
        self,
        path: Union[NameRequired, str],
        *extra: Union[NameRequired, str],
        endpoint: Union[
            Callable[P_HandlerParams, T_HandlerReturn],
            HandlerCallWrapper[P_HandlerParams, T_HandlerReturn],
        ],
        broker: BrokerAsyncUsecase[Any, Any],
        dependencies: Sequence[params.Depends] = (),
        dependency_overrides_provider: Optional[Any] = None,
        **handle_kwargs: AnyDict,
    ) -> None:
        self.path = path
        self.broker = broker

        path_name = (path if isinstance(path, str) else path.name) or ""

        if isinstance(endpoint, HandlerCallWrapper):
            orig_call = endpoint._original_call
        else:
            orig_call = endpoint

        dependant = get_dependant(
            path=path_name,
            call=orig_call,
        )
        for depends in dependencies[::-1]:
            dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=path_name),
            )
        self.dependant = dependant

        call = wraps(orig_call)(
            PropanMessage.get_session(
                dependant,
                dependency_overrides_provider,
            )
        )

        if isinstance(endpoint, HandlerCallWrapper):
            endpoint._original_call = call
            handler = endpoint

        else:
            handler = call

        self.handler = broker.subscriber(
            path,
            *extra,
            _raw=True,
            _get_dependant=lambda call: dependant,
            **handle_kwargs,  # type: ignore
        )(handler)


class PropanMessage(Request):
    scope: AnyDict
    _cookies: AnyDict
    _headers: AnyDict  # type: ignore
    _body: AnyDict  # type: ignore
    _query_params: AnyDict  # type: ignore

    def __init__(
        self,
        body: Optional[AnyDict] = None,
        headers: Optional[AnyDict] = None,
    ):
        self.scope = {}
        self._cookies = {}
        self._headers = headers or {}
        self._body = body or {}
        self._query_params = self._body

    @classmethod
    def get_session(
        cls,
        dependant: Dependant,
        dependency_overrides_provider: Optional[Any] = None,
    ) -> Callable[[NativeMessage[Any]], Any]:
        assert dependant.call
        func = get_app(dependant, dependency_overrides_provider)

        dependencies_names = tuple(i.name for i in dependant.dependencies)

        first_arg = next(
            dropwhile(
                lambda i: i in dependencies_names,
                inspect.signature(dependant.call).parameters,
            ),
            None,
        )

        async def app(message: NativeMessage[Any]) -> Any:
            body = message.decoded_body
            if first_arg is not None:
                if not isinstance(body, dict):  # pragma: no branch
                    fastapi_body: AnyDict = {first_arg: body}
                else:
                    fastapi_body = body

                session = cls(fastapi_body, message.headers)
            else:
                session = cls()
            return await func(session)

        return app


def get_app(
    dependant: Dependant,
    dependency_overrides_provider: Optional[Any] = None,
) -> Callable[[PropanMessage], Coroutine[Any, Any, Any]]:
    async def app(request: PropanMessage) -> Any:
        async with AsyncExitStack() as stack:
            request.scope["fastapi_astack"] = stack

            solved_result = await solve_dependencies(
                request=request,
                body=request._body,
                dependant=dependant,
                dependency_overrides_provider=dependency_overrides_provider,
            )

            values, errors, _, _2, _3 = solved_result
            if errors:
                raise_fastapi_validation_error(errors, request._body)

            return await run_endpoint_function(
                dependant=dependant,
                values=values,
                is_coroutine=asyncio.iscoroutinefunction(dependant.call),
            )

    return app
