import asyncio
import logging
import sys
from typing import (
    Optional, Callable, NoReturn,
    List, Dict, Any
)

if sys.platform not in ('win32', 'cygwin', 'cli'):
    import uvloop
    uvloop.install()

from propan.log import logger
from propan.utils.classes import Singlethon
from propan.utils.context import use_context, context
from propan.utils.functions import call_or_await
from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.cli.supervisors.utils import set_exit


class PropanApp(Singlethon):
    _context: Dict[str, Any] = {}
    _on_startup_calling: List[Callable] = []
    _on_shutdown_calling: List[Callable] = []

    def __init__(
        self,
        broker: Optional[BrokerUsecase] = None,
        logger: logging.Logger = logger
    ):
        self.broker = broker
        self.logger = logger
        self.context = context

        context.set_context("app", self)

        self.loop = asyncio.get_event_loop()
    
    def set_broker(self, broker: BrokerUsecase):
        self.broker = broker

    def on_startup(self, func: Callable):
        self._on_startup_calling.append(use_context(func))
        return func

    def on_shutdown(self, func: Callable):
        self._on_shutdown_calling.append(use_context(func))
        return func

    def run(self, log_level: int = logging.INFO, **context_kwargs) -> NoReturn:
        for k, v in context_kwargs.items():
            self.context.set_context(k, v)

        set_exit(lambda *_: self.loop.stop())
        self._start(log_level)
        self._stop(log_level)  # calls after loop stopping
            
    def _start(self, log_level: int) -> NoReturn:
        self.logger.log(log_level, "Propan app starting...")
        self.loop.run_until_complete(self._startup())
        self.logger.log(log_level, "Propan app started successfully! To exit press CTRL+C")
        self.loop.run_forever()

    def _stop(self, log_level: int):
        self.logger.log(log_level, "Propan app shutting down...")
        self.loop.run_until_complete(self._shutdown())
        self.logger.log(log_level, "Propan app shut down gracefully.")

    async def _startup(self):
        if (broker := self.broker) is not None:
            await broker.start()

        for func in self._on_startup_calling:
            await call_or_await(func)

    async def _shutdown(self):
        if getattr(self.broker, "_connection", False) is not False:
            await self.broker.close()

        for func in self._on_shutdown_calling:
            await call_or_await(func)
