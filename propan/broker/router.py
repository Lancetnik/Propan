from abc import abstractmethod
from typing import Any, Callable, Dict, Generic, List

from typing_extensions import ParamSpec

from propan.broker.publisher import BasePublisher
from propan.broker.types import MsgType
from propan.broker.wrapper import HandlerCallWrapper
from propan.types import AnyDict, SendableReturn

P_RouteCall = ParamSpec("P_RouteCall")


class BrokerRoute(Generic[MsgType, SendableReturn]):
    call: Callable[..., SendableReturn]
    args: Any
    kwargs: AnyDict

    def __init__(
        self,
        call: Callable[..., SendableReturn],
        *,
        args: Any,
        kwargs: AnyDict,
    ):
        self.call = call
        self.args = args
        self.kwargs = kwargs


class BrokerRouter(Generic[MsgType]):
    prefix: str
    _handlers: List[BrokerRoute[MsgType, Any]]
    _publishers: Dict[Any, BrokerRoute[MsgType, Any]]

    def __init__(
        self,
        prefix: str = "",
    ):
        self.prefix = prefix
        self._handlers = []
        self._publishers = {}

    @abstractmethod
    def subscriber(
        self,
        subj: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, SendableReturn]],
        HandlerCallWrapper[P_RouteCall, SendableReturn],
    ]:
        raise NotImplementedError()

    def _wrap_subscriber(
        self, *args: Any, **kwargs: AnyDict
    ) -> Callable[
        [Callable[P_RouteCall, SendableReturn]],
        HandlerCallWrapper[P_RouteCall, SendableReturn],
    ]:
        def router_subscriber_wrapper(
            func: Callable[P_RouteCall, SendableReturn]
        ) -> HandlerCallWrapper[P_RouteCall, SendableReturn]:
            func = HandlerCallWrapper(func)
            route: BrokerRoute[MsgType, SendableReturn] = BrokerRoute(
                call=func,
                args=args,
                kwargs=kwargs,
            )
            self._handlers.append(route)
            return func

        return router_subscriber_wrapper

    @abstractmethod
    def publisher(
        self,
        subj: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> BasePublisher:
        raise NotImplementedError()
