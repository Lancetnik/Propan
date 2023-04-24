from typing import Any, Callable, Optional

from core.router import MQRouter

class RabbitRouter(MQRouter):
    def add_api_mq_route(
        self,
        queue: str,
        *,
        endpoint: Callable[..., Any],
        exchange: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        pass
    def event(
        self, queue: str, *, exchange: Optional[str] = None, name: Optional[str] = None
    ) -> None:
        pass
