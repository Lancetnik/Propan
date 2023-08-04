from functools import partial, wraps
from typing import Any, Callable, ContextManager, Optional
from unittest.mock import MagicMock

import anyio

from propan.broker.core.abc import BrokerUsecase
from propan.broker.handler import AsyncHandler
from propan.broker.message import PropanMessage
from propan.broker.types import MsgType
from propan.types import DecodedMessage, F_Return


def patch_broker_calls(broker: BrokerUsecase[Any, Any]) -> None:
    for handler in broker.handlers.values():
        calls = []
        for (
            wrapper,
            wrapped_f,
            filter_f,
            parser,
            decoder,
            middlewares,
            dep,
        ) in handler.calls:
            mock = MagicMock()
            calls.append(
                (
                    wrapper,
                    partial(_wrap_handler_mock(mock, wrapped_f), reraise_exc=True),
                    filter_f,
                    parser,
                    decoder,
                    middlewares,
                    dep,
                )
            )

        handler.calls = calls  # type: ignore


async def call_handler(
    handler: AsyncHandler[Any],
    message: Any,
    rpc: bool = False,
    rpc_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Optional[DecodedMessage]:
    scope: Callable[[Optional[float], bool], ContextManager[Any]]
    if raise_timeout:
        scope = anyio.fail_after
    else:
        scope = anyio.move_on_after

    with scope(rpc_timeout):
        result = await handler.consume(message)

        if rpc is True:
            return result

    return None


def _wrap_handler_mock(
    mock: MagicMock, func: Callable[[PropanMessage[MsgType], bool], F_Return]
) -> Callable[[PropanMessage[MsgType], bool], F_Return]:
    @wraps(func)
    def _patched_call(
        msg: PropanMessage[MsgType],
        reraise_exc: bool = False,
    ) -> F_Return:
        mock(msg.decoded_body)
        return func(msg, reraise_exc)

    return _patched_call
