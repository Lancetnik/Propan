from abc import abstractmethod
from typing import Any, Callable, Generic, List

from typing_extensions import ParamSpec, TypeVar

from propan.types import AnyDict, SendableMessage

P_RouteCall = ParamSpec("P_RouteCall")
T_RouteReturn = TypeVar("T_RouteReturn", bound=SendableMessage)
MsgType = TypeVar("MsgType")


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

    def __call__(self, msg: MsgType, reraise_exc: bool = False) -> T_RouteReturn:
        return self.call(msg, reraise_exc)


class BrokerRouter(Generic[MsgType]):
    prefix: str
    handlers: List[BrokerRoute[MsgType, Any]]

    def __init__(
        self,
        prefix: str = "",
    ):
        self.prefix = prefix
        self.handlers = []

    @abstractmethod
    def handle(
        self,
        *args: Any,
        **kwargs: AnyDict,
    ) -> Callable[
        [Callable[P_RouteCall, T_RouteReturn]],
        Callable[[MsgType, bool], T_RouteReturn],
    ]:
        def router_hanle_wrapper(
            func: Callable[P_RouteCall, T_RouteReturn]
        ) -> BrokerRoute[MsgType, T_RouteReturn]:
            router = BrokerRoute(
                call=func,
                args=args,
                kwargs=kwargs,
            )
            self.handlers.append(router)
            return router

        return router_hanle_wrapper
