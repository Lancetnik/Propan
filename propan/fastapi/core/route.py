import asyncio
import inspect
from functools import wraps
from itertools import dropwhile
from typing import Any, Callable, Coroutine, List, Optional, Sequence, Union

from fastapi import __version__ as FASTAPI_VERSION
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
from typing_extensions import Never

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage as NativeMessage
from propan.brokers._model.schemas import Queue
from propan.types import AnyDict

if FASTAPI_VERSION.startswith("0.10"):
    from fastapi._compat import _normalize_errors
    from fastapi.exceptions import ResponseValidationError

    def raise_error(errors: List[Any], body: AnyDict) -> Never:
        raise ResponseValidationError(_normalize_errors(errors), body=body)

else:
    from pydantic import ValidationError, create_model

    ROUTER_VALIDATION_ERROR_MODEL = create_model("PropanRoute")

    def raise_error(errors: List[Any], body: AnyDict) -> Never:
        raise ValidationError(errors, ROUTER_VALIDATION_ERROR_MODEL)


class PropanRoute(BaseRoute):
    def __init__(
        self,
        path: Union[Queue, str],
        *extra: Union[Queue, str],
        endpoint: Callable[..., Any],
        broker: BrokerUsecase[Any, Any],
        dependencies: Sequence[params.Depends] = (),
        dependency_overrides_provider: Optional[Any] = None,
        **handle_kwargs: AnyDict,
    ) -> None:
        self.path = path
        self.broker = broker

        path_name = (path if isinstance(path, str) else path.name) or ""
        dependant = get_dependant(
            path=path_name,
            call=endpoint,
        )
        for depends in dependencies[::-1]:
            dependant.dependencies.insert(
                0,
                get_parameterless_sub_dependant(depends=depends, path=path_name),
            )

        handler = wraps(endpoint)(
            PropanMessage.get_session(
                dependant,
                dependency_overrides_provider,
            )
        )

        self.dependant = dependant

        self.handler = broker.handle(
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
        solved_result = await solve_dependencies(
            request=request,
            body=request._body,
            dependant=dependant,
            dependency_overrides_provider=dependency_overrides_provider,
        )

        values, errors, _, _2, _3 = solved_result
        if errors:
            raise_error(errors, request._body)

        return await run_endpoint_function(
            dependant=dependant,
            values=values,
            is_coroutine=asyncio.iscoroutinefunction(dependant.call),
        )

    return app
