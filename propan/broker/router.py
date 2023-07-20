from abc import abstractmethod
from typing import Any, Callable, Generic, List

from typing_extensions import ParamSpec, TypeVar

from propan.broker.schemas import HandlerCallWrapper, Publisher
from propan.broker.types import MsgType
from propan.types import AnyDict, SendableMessage

P_RouteCall = ParamSpec("P_RouteCall")
T_RouteReturn = TypeVar("T_RouteReturn", bound=SendableMessage)


class BrokerRoute(Generic[MsgType, T_RouteReturn]):
    call: Callable[P_RouteCall, T_RouteReturn]
    args: Any
    kwargs: AnyDict

    def __init__(
        self,
        call: Callable[P_RouteCall, T_RouteReturn],
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
    _publishers: List[BrokerRoute[MsgType, Any]]

    def __init__(
        self,
        prefix: str = "",
    ):
        self.prefix = prefix
        self._handlers = []
        self._publishers = []

    @abstractmethod
    def subscriber(
        self,
        subj: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        HandlerCallWrapper[P_RouteCall, T_RouteReturn],
    ]:
        raise NotImplementedError()

    def _wrap_subscriber(
        self, *args: Any, **kwargs: AnyDict
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        HandlerCallWrapper[P_RouteCall, T_RouteReturn],
    ]:
        def router_subscriber_wrapper(
            func: Callable[P_RouteCall, T_RouteReturn]
        ) -> BrokerRoute[MsgType, T_RouteReturn]:
            func = HandlerCallWrapper(func)
            route = BrokerRoute(
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
    ) -> Publisher:
        raise NotImplementedError()
