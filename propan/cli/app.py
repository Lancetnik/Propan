import asyncio
import logging
import sys
from typing import Any, Callable, Dict, List, Optional

if sys.platform not in ("win32", "cygwin", "cli"):
    import uvloop

    uvloop.install()

from anyio import create_memory_object_stream, create_task_group
from anyio.streams.memory import MemoryObjectReceiveStream
from propan.brokers.model.broker_usecase import BrokerUsecase
from propan.cli.supervisors.basereload import BaseReload
from propan.cli.supervisors.utils import set_exit
from propan.log import logger
from propan.utils.classes import Singlethon
from propan.utils.context import context, use_context
from propan.utils.functions import call_or_await


class PropanApp(Singlethon, BaseReload):
    _context: Dict[str, Any] = {}
    _on_startup_calling: List[Callable[..., None]] = []
    _on_shutdown_calling: List[Callable[..., None]] = []

    def __init__(
        self, broker: Optional[BrokerUsecase] = None, logger: logging.Logger = logger
    ):
        super().__init__(None, [], None)
        self.broker = broker
        self.logger = logger
        self.context = context

        context.set_context("app", self)

        self.loop = asyncio.get_event_loop()

    def set_broker(self, broker: BrokerUsecase) -> None:
        self.broker = broker

    def on_startup(self, func: Callable[..., None]) -> Callable[..., None]:
        self._on_startup_calling.append(use_context(func))
        return func

    def on_shutdown(self, func: Callable[..., None]) -> Callable[..., None]:
        self._on_shutdown_calling.append(use_context(func))
        return func

    async def run(self, log_level: int = logging.INFO, **context_kwargs: Any) -> None:
        for k, v in context_kwargs.items():
            self.context.set_context(k, v)

        send_stream, receive_stream = create_memory_object_stream()

        async with create_task_group() as tg:
            set_exit(lambda *_: tg.start_soon(send_stream.send, True))
            tg.start_soon(self._stop, log_level, receive_stream)
            tg.start_soon(self._start, log_level)

    async def _start(self, log_level: int) -> None:
        self.logger.log(log_level, "Propan app starting...")
        await self._startup()
        self.logger.log(
            log_level, "Propan app started successfully! To exit press CTRL+C"
        )

    async def _stop(
        self, log_level: int, receive_stream: MemoryObjectReceiveStream
    ) -> None:
        await receive_stream.receive()
        self.logger.log(log_level, "Propan app shutting down...")
        await self._shutdown()
        self.logger.log(log_level, "Propan app shut down gracefully.")
        exit()

    async def _startup(self) -> None:
        for func in self._on_startup_calling:
            await call_or_await(func)

        if self.broker is not None:
            await self.broker.start()

    async def _shutdown(self) -> None:
        if (
            self.broker is not None
            and getattr(self.broker, "_connection", False) is not False
        ):
            await self.broker.close()

        for func in self._on_shutdown_calling:
            await call_or_await(func)
