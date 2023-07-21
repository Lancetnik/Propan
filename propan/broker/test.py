from functools import partial, wraps
from typing import Any, Optional
from unittest.mock import MagicMock

import anyio

from propan.broker.core.abc import BrokerUsecase
from propan.broker.handler import AsyncHandler
from propan.broker.message import PropanMessage


def patch_broker_calls(broker: BrokerUsecase) -> None:
    original_handlers = tuple(broker.handlers.values())
    for handler in original_handlers:
        calls = []
        for wrapper, wrapped_f, filter_f, parser, decoder, middlewares in handler.calls:
            mock = MagicMock()
            calls.append(
                (
                    wrapper,
                    _wrap_handler_mock(mock, partial(wrapped_f, reraise_exc=True)),
                    filter_f,
                    parser,
                    decoder,
                    middlewares,
                )
            )

        handler.calls = calls


async def call_handler(
    handler: AsyncHandler,
    message: Any,
    rpc: bool = False,
    rpc_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    if raise_timeout:
        scope = anyio.fail_after
    else:
        scope = anyio.move_on_after

    result: Any = None
    with scope(rpc_timeout):
        result = await handler.consume(message)

    if rpc is True:  # pragma: no branch
        return result


def _wrap_handler_mock(mock: MagicMock, func):
    @wraps(func)
    def _patched_call(msg: PropanMessage[Any]) -> Any:
        mock(msg.decoded_body)
        return func(msg)

    return _patched_call
