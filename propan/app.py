import asyncio
from functools import partial, wraps
from typing import Optional, List, Callable
from pathlib import Path
import inspect

from propan.logger import ignore_exceptions, empty
from propan.logger.model.usecase import LoggerUsecase

from propan.config import init_settings

from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.annotations import apply_types


class PropanApp:
    _instanse = None

    apply_types = staticmethod(apply_types)

    def __new__(cls, *args, **kwargs):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse

    def __init__(
        self,
        broker: Optional[BrokerUsecase] = None,
        logger: LoggerUsecase = empty,
        settings_dir: Optional[Path] = None,
        apply_types=False,
        *args, **kwargs
    ):
        if settings_dir:
            self.settings = init_settings(settings_dir, settings_dir="")

        self.broker = broker
        self.logger = logger

        self._is_apply_types: bool = apply_types
        self._on_startup_calling: List[Callable] = []
        self._on_shutdown_calling: List[Callable] = []
        self.loop = asyncio.get_event_loop()

        self.ignore_exceptions = staticmethod(partial(
            ignore_exceptions, logger=logger
        ))

    async def startup(self):
        if (broker := self.broker) is not None:
            self.logger.info(f"Listening: {', '.join(broker.handlers.keys())} queues")
            await broker.connect()
            await broker.init_channel()
            await broker.start()

        for func in self._on_startup_calling:
            f = func()
            if inspect.isawaitable(f):
                await f

    async def shutdown(self):
        if getattr(self.broker, "_connection", False) is not False:
            await self.broker.close()

        for func in self._on_shutdown_calling:
            f = func()
            if inspect.isawaitable(f):
                await f

    def run(self):
        try:
            self.logger.info("Propan app starting...")
            self.loop.run_until_complete(self.startup())
            self.logger.success("Propan app started successfully!")

            self.loop.run_forever()
        finally:
            self.logger.info("Propan app shutting down...")
            self.loop.run_until_complete(self.shutdown())

    def handle(self, queue_name: str):
        def decor(func):
            if self._is_apply_types:
                func = wraps(func)(apply_types(func))

            self.broker.handlers[queue_name] = func
        return decor

    def on_startup(self, func: Callable):
        self._on_startup_calling.append(func)
        return func

    def on_shutdown(self, func: Callable):
        self._on_shutdown_calling.append(func)
        return func
