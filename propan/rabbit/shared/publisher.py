from typing import Callable, Optional, Union, Any

from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import P_HandlerParams, T_HandlerReturn
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.rabbit.types import TimeoutType
from propan.types import AnyDict
from propan.utils.functions import call_or_await


class Publisher(HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]):
    queue: Union[RabbitQueue, str]
    exchange: Union[RabbitExchange, str, None]
    routing_key: str
    mandatory: bool
    immediate: bool
    persist: bool
    reply_to: Optional[str]
    message_kwargs: AnyDict

    def __init__(
        self,
        call: Union[
            Callable[P_HandlerParams, T_HandlerReturn],
            HandlerCallWrapper[P_HandlerParams, T_HandlerReturn]
        ],
        publish: Callable[..., Any],
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: TimeoutType = None,
        persist: bool = False,
        reply_to: Optional[str] = None,
        **message_kwargs: AnyDict,
    ):
        super().__init__(call)
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.mandatory = mandatory
        self.immediate = immediate
        self.timeout = timeout
        self.persist = persist
        self.reply_to = reply_to
        self.message_kwargs = message_kwargs
        self.publish = publish

    # async def __call__(
    #     self,
    #     *args: P_HandlerParams.args,
    #     **kwargs: P_HandlerParams.kwargs,
    # ) -> T_HandlerReturn:
    #     result = await call_or_await(self.original_call, *args, **kwargs)

    #     try:
    #         await self.publish(
    #             message=result,
    #             queue=self.queue,
    #             exchange=self.exchange,
    #             routing_key=self.routing_key,
    #             mandatory=self.mandatory,
    #             immediate=self.immediate,
    #             timeout=self.timeout,
    #             persist=self.persist,
    #             reply_to=self.reply_to,
    #             **self.message_kwargs,
    #         )
    #     except Exception as e:
    #         self._log(
    #             f"Publish exception: {e}",
    #             logging.ERROR,
    #             self._get_log_context(
    #                 context.get_local("message"), r_queue, r_exchange
    #             ),
    #         )

    #     return result
