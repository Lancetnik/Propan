from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar

from fastapi.dependencies.utils import get_dependant
from starlette.requests import Request
from starlette.routing import get_name

NativeMessage = TypeVar("NativeMessage")


class MQRoute(ABC):
    @abstractmethod
    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.name = name if name else get_name(endpoint)
        self.dependant = get_dependant(path=path, call=self.endpoint)

    @abstractmethod
    async def init_handler(self) -> None:
        raise NotImplementedError()


class MQMessage(Request):
    message: Any
    message_id: str

    def __init__(self):
        self.scope = {}
        self._cookies = {}


def get_session(
    connection_class: MQRoute, func: Callable[[MQRoute], None]
) -> Callable[[NativeMessage], None]:
    async def app(message: NativeMessage) -> None:
        session = connection_class(message)
        await func(session)

    return app
