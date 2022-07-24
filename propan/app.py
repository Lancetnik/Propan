import asyncio
from functools import partial, wraps
from typing import Optional
from pathlib import Path

from propan.logger import ignore_exceptions
from propan.logger.model.usecase import LoggerUsecase
from propan.logger.adapter.empty import EmptyLogger

from propan.config import init_settings

from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.annotations import apply_types


class PropanApp:
    _instanse = None

    apply_types = wraps(apply_types)(staticmethod(apply_types))

    def __new__(cls, *args, **kwargs):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse

    def __init__(
        self,
        broker: Optional[BrokerUsecase] = None,
        logger: LoggerUsecase = EmptyLogger(),
        settings_dir: Optional[Path] = None,
        apply_types=False,
        *args, **kwargs
    ):
        if settings_dir:
            self.settings = init_settings(settings_dir, settings_dir="")
        
        self.broker = broker
        self._apply_types = apply_types
        self.loop = asyncio.get_event_loop()
        self.logger = logger

        self.ignore_exceptions = wraps(ignore_exceptions)(staticmethod(partial(
            ignore_exceptions, logger=logger
        )))

    async def startup(self):
        if (broker := self.broker) is not None:
            self.logger.info(f"Listening: {', '.join(broker.handlers.keys())} queues")
            await broker.connect()
            await broker.init_channel()
            await broker.start()

    async def shutdown(self):
        if getattr(self.broker, "_connection", False) is not False:
            await self.broker.close()

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
            if self._apply_types:
                func = wraps(func)(apply_types(func))
            self.broker.handlers[queue_name] = func
        return decor
