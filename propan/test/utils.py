from typing import Any, Optional

import anyio

from propan.brokers._model.schemas import BaseHandler


async def call_handler(
    handler: BaseHandler,
    message: Any,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    if raise_timeout:
        scope = anyio.fail_after
    else:
        scope = anyio.move_on_after

    result: Any = None
    with scope(callback_timeout):
        result = await handler.callback(message)

    if callback is True:  # pragma: no branch
        return result
