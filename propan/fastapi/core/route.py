import asyncio
import inspect
from itertools import dropwhile
from typing import Any, Callable, Coroutine, Optional, Union

from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from fastapi.routing import run_endpoint_function
from pydantic import ValidationError, create_model
from starlette.requests import Request
from starlette.routing import BaseRoute, get_name

from propan.brokers.model import BrokerUsecase
from propan.types import AnyDict

NativeMessage = Union[str, AnyDict, bytes]


class PropanRoute(BaseRoute):
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        broker: BrokerUsecase,
        *,
        name: Optional[str] = None,
        dependency_overrides_provider: Optional[Any] = None,
        **hanle_kwargs: AnyDict,
    ) -> None:
        self.broker = broker
        self.path = path
        self.endpoint = endpoint
        self.name = name if name else get_name(endpoint)
        self.dependant = get_dependant(path=path, call=self.endpoint)

        handler = PropanMessage.get_session(
            self.dependant, dependency_overrides_provider
        )
        broker.handle(path, **hanle_kwargs)(handler)  # type: ignore


class PropanMessage(Request):
    scope: AnyDict
    _cookies: AnyDict
    _headers: AnyDict       # type: ignore
    _body: AnyDict          # type: ignore
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
        connection_class,
        dependant: Dependant,
        dependency_overrides_provider: Optional[Any] = None,
    ) -> Callable[[NativeMessage], Any]:
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

        async def app(message: NativeMessage) -> Any:
            if first_arg is not None:
                if not isinstance(message, dict):  # pragma: no branch
                    message = {first_arg: message}

                session = connection_class(message)
            else:
                session = connection_class()
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
            raise ValidationError(errors, create_model("MQRoute"))

        return await run_endpoint_function(
            dependant=dependant,
            values=values,
            is_coroutine=asyncio.iscoroutinefunction(dependant.call),
        )

    return app
