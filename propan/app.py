import asyncio
from typing import (
    Optional, Callable, NoReturn,
    List, Dict, Any
)
from pathlib import Path

from propan.logger import empty
from propan.logger.model.usecase import LoggerUsecase

from propan.config import init_settings
from propan.utils.classes import Singlethon
from propan.utils.context import use_context, context
from propan.utils.functions import call_or_await
from propan.brokers.model.bus_usecase import BrokerUsecase


class PropanApp(Singlethon):
    _context: Dict[str, Any] = {}
    _on_startup_calling: List[Callable] = []
    _on_shutdown_calling: List[Callable] = []

    def __init__(
        self,
        broker: Optional[BrokerUsecase] = None,
        logger: LoggerUsecase = empty,
        settings_dir: Optional[Path] = None,
        *args, **kwargs
    ):
        if settings_dir:
            self.settings = init_settings(settings_dir, settings_dir="")

        self.broker = broker
        self.logger = logger

        self.loop = asyncio.get_event_loop()

        context.set_context("app", self)
        context.set_context("broker", self.broker)
        context.set_context("logger", self.logger)

    def on_startup(self, func: Callable):
        self._on_startup_calling.append(use_context(func))
        return func

    def on_shutdown(self, func: Callable):
        self._on_shutdown_calling.append(use_context(func))
        return func

    def run(self) -> NoReturn:
        try:
            self.logger.info("Propan app starting...")
            self.loop.run_until_complete(self._startup())
            self.logger.info("Propan app started successfully! To exit press CTRL+C")
            self.loop.run_forever()
        finally:
            self.logger.info("Propan app shutting down...")
            self.loop.run_until_complete(self._shutdown())
            self.logger.info("Propan app shut down gracefully.")

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