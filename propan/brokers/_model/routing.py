from typing import Any, List

from propan.types import AnyDict, HandlerCallable, HandlerWrapper


class BrokerRoute:
    def __init__(
        self,
        call: HandlerCallable,
        *,
        args: Any,
        kwargs: AnyDict,
    ):
        self.call = call
        self.args = args
        self.kwargs = kwargs


class BrokerRouter:
    prefix: str
    handlers: List[BrokerRoute]

    def __init__(
        self,
        prefix: str = "",
    ):
        self.prefix = prefix
        self.handlers = []

    def handle(
        self,
        subj: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> HandlerWrapper:
        def router_hanle_wrapper(func: HandlerCallable) -> HandlerCallable:
            router = BrokerRoute(
                call=func,
                args=(self.prefix + subj, *args),
                kwargs=kwargs,
            )
            self.handlers.append(router)
            return func

        return router_hanle_wrapper
