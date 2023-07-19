from abc import abstractmethod
from typing import Any, Callable, Generic, List

from typing_extensions import ParamSpec, TypeVar

from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import MsgType, P_HandlerParams, T_HandlerReturn
from propan.types import AnyDict, SendableMessage

P_RouteCall = ParamSpec("P_RouteCall")
T_RouteReturn = TypeVar("T_RouteReturn", bound=SendableMessage)


class BrokerRoute(Generic[MsgType, T_RouteReturn]):
    call: Callable[P_RouteCall, T_RouteReturn]

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

    def __call__(
        self,
        msg: MsgType,
        reraise_exc: bool = False,
    ) -> T_RouteReturn:
        return self.call(msg, reraise_exc)


class BrokerRouter(Generic[MsgType]):
    prefix: str
    handlers: List[BrokerRoute[MsgType, Any]]
    publishers: List[BrokerRoute[MsgType, Any]]

    def __init__(
        self,
        prefix: str = "",
    ):
        self.prefix = prefix
        self.handlers = []
        self.publishers = []

    @abstractmethod
    def subscriber(
        self,
        subj: str,
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        Callable[[MsgType, bool], T_RouteReturn],
    ]:
        raise NotImplementedError()

    def _wrap_subscriber(
        self, *args: Any, **kwargs: AnyDict
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        Callable[[MsgType, bool], T_RouteReturn],
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
            self.handlers.append(route)
            return func

        return router_subscriber_wrapper

    def _wrap_publisher(
        self, *args: Any, **kwargs: AnyDict
    ) -> Callable[
        [Callable[P_HandlerParams, T_HandlerReturn]],
        Callable[P_HandlerParams, T_HandlerReturn],
    ]:
        def router_publisher_wrapper(
            func: Callable[P_RouteCall, T_RouteReturn]
        ) -> BrokerRoute[MsgType, T_RouteReturn]:
            func = HandlerCallWrapper(func)
            route = BrokerRoute(
                call=func,
                args=args,
                kwargs=kwargs,
            )
            self.publishers.append(route)
            return func

        return router_publisher_wrapper
