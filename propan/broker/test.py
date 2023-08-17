from types import TracebackType
from typing import Any, Callable, ContextManager, Dict, Optional, Type

import anyio
from anyio.abc._tasks import TaskGroup

from propan.app import PropanApp
from propan.broker.core.abc import BrokerUsecase
from propan.broker.handler import AsyncHandler
from propan.types import SendableMessage, SettingField


class TestApp:
    app: PropanApp
    _extra_options: Optional[Dict[str, SettingField]]
    _event: anyio.Event
    _task: TaskGroup

    def __init__(
        self,
        app: PropanApp,
        run_extra_options: Optional[Dict[str, SettingField]] = None,
    ) -> None:
        self.app = app
        self._extra_options = run_extra_options

    async def __aenter__(self) -> PropanApp:
        self.app._stop_event = self._event = anyio.Event()
        await self.app._start(run_extra_options=self._extra_options)
        self._task = tg = anyio.create_task_group()
        await tg.__aenter__()
        tg.start_soon(self.app._stop)
        return self.app

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        self._event.set()
        await self._task.__aexit__(exc_type, exc_val, exec_tb)


def patch_broker_calls(broker: BrokerUsecase[Any, Any]) -> None:
    for handler in broker.handlers.values():
        handler.set_test()


async def call_handler(
    handler: AsyncHandler[Any],
    message: Any,
    rpc: bool = False,
    rpc_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Optional[SendableMessage]:
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
