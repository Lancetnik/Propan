import asyncio

from  propan.event_bus.model.bus_usecase import EventBusUsecase


class PropanApp:
    _instanse = None
    loop = None

    def __new__(cls, *args, **kwargs):
        if cls._instanse is None:
            cls._instanse = super().__new__(cls)
        return cls._instanse
    
    def __init__(self, queue_adapter: EventBusUsecase, *args, **kwargs):
        self.loop = asyncio.get_event_loop()
        self.queue_adapter = queue_adapter

    def run(self):
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.queue_adapter.close())
    
    def queue_handler(self, queue_name: str):
        def decor(func):
            self.loop.run_until_complete(
                self.queue_adapter.set_queue_handler(
                    queue_name=queue_name,
                    handler=func
                )
            )
        return decor
