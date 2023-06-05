import asyncio
import logging
from typing import Dict, List, Optional

from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from typing_extensions import Protocol

from propan.cli.supervisors.utils import set_exit
from propan.cli.utils.parser import SettingField
from propan.log import logger
from propan.types import AnyCallable, AsyncFunc
from propan.utils import apply_types, context
from propan.utils.functions import to_async


class Runnable(Protocol):
    async def start(self) -> None:
        ...

    async def close(self) -> None:
        ...


class PropanApp:
    _on_startup_calling: List[AsyncFunc]
    _after_startup_calling: List[AsyncFunc]
    _on_shutdown_calling: List[AsyncFunc]
    _after_shutdown_calling: List[AsyncFunc]

    _stop_stream: Optional[MemoryObjectSendStream[bool]]
    _receive_stream: Optional[MemoryObjectReceiveStream[bool]]

    def __init__(
        self,
        broker: Optional[Runnable] = None,
        logger: Optional[logging.Logger] = logger,
        # AsyncAPI args,
        title: str = "Propan",
        version: str = "0.1.0",
        description: str = "",
    ):
        self.broker = broker
        self.logger = logger
        self.context = context
        context.set_global("app", self)

        self._on_startup_calling = []
        self._after_startup_calling = []
        self._on_shutdown_calling = []
        self._after_shutdown_calling = []
        self._stop_stream = None
        self._receive_stream = None
        self._command_line_options: Dict[str, SettingField] = {}

        self.title = title
        self.version = version
        self.description = description

    def set_broker(self, broker: Runnable) -> None:
        self.broker = broker

    def on_startup(self, func: AnyCallable) -> AnyCallable:
        return _set_async_hook(self._on_startup_calling, func)

    def on_shutdown(self, func: AnyCallable) -> AnyCallable:
        return _set_async_hook(self._on_shutdown_calling, func)

    def after_startup(self, func: AnyCallable) -> AnyCallable:
        return _set_async_hook(self._after_startup_calling, func)

    def after_shutdown(self, func: AnyCallable) -> AnyCallable:
        return _set_async_hook(self._after_shutdown_calling, func)

    async def run(self, log_level: int = logging.INFO) -> None:
        self._init_async_cycle()
        async with create_task_group() as tg:
            set_exit(lambda *_: tg.start_soon(self.__exit, True))
            tg.start_soon(self._stop, log_level)
            tg.start_soon(self._start, log_level)

    def _init_async_cycle(self) -> None:
        self.loop = asyncio.get_event_loop()
        if not self._stop_stream and not self._receive_stream:
            self._stop_stream, self._receive_stream = create_memory_object_stream(1)

    async def _start(self, log_level: int = logging.INFO) -> None:
        self._log(log_level, "Propan app starting...")
        await self._startup()
        self._log(log_level, "Propan app started successfully! To exit press CTRL+C")

    async def _stop(self, log_level: int = logging.INFO) -> None:
        assert self._receive_stream, "You should call `_init_async_cycle` first"
        await self._receive_stream.receive()
        self._log(log_level, "Propan app shutting down...")
        await self._shutdown()
        self._log(log_level, "Propan app shut down gracefully.")

    def _log(self, level: int, message: str) -> None:
        if self.logger is not None:
            self.logger.log(level, message)

    async def _startup(self) -> None:
        for func in self._on_startup_calling:
            await func(**self._command_line_options)

        if self.broker is not None:
            await self.broker.start()

        for func in self._after_startup_calling:
            await func()

    async def _shutdown(self) -> None:
        for func in self._on_shutdown_calling:
            await func()

        if (
            self.broker is not None
            and getattr(self.broker, "_connection", False) is not False
        ):
            await self.broker.close()

        for func in self._after_shutdown_calling:
            await func()

    async def __exit(self, flag: bool) -> None:
        if self._stop_stream is not None:  # pragma: no branch
            await self._stop_stream.send(flag)


def _set_async_hook(hooks: List[AsyncFunc], func: AnyCallable) -> AnyCallable:
    f: AsyncFunc = apply_types(to_async(func))
    hooks.append(f)
    return func
