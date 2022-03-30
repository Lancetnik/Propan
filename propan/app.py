import asyncio

from propan.brokers import RabbitBroker
from propan.logger import loguru as logger

from propan.brokers.model.bus_usecase import BrokerUsecase
from propan.annotations import apply_types


class PropanApp:
    _instanse = None

    def __new__(cls, *args, **kwargs):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse

    def __init__(
        self,
        broker: BrokerUsecase = None,
        apply_types=False,
        *args, **kwargs
    ):
        self.broker = broker or RabbitBroker(logger=logger)
        self._apply_types = apply_types
        self.loop = asyncio.get_event_loop()

    def run(self):
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.broker.close())

    def handle(self, queue_name: str):
        def decor(func):
            if self._apply_types:
                func = apply_types(func)
            self.loop.run_until_complete(
                self.broker.set_queue_handler(
                    queue_name=queue_name,
                    handler=func
                )
            )
        return decor
