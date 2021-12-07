from typing import Protocol, NoReturn, Callable

from propan.logger.model.usecase import LoggerUsecase

from propan.event_bus.model.bus_connection import ConnectionData


class EventBusUsecase(Protocol):
    def connect(self, connection_data: ConnectionData):
        raise NotImplementedError()

    def init_channel(self) -> NoReturn:
        raise NotImplementedError()

    def publish_message(self, queue_name: str, message: str) -> NoReturn:
        raise NotImplementedError()

    def process_message(logger: LoggerUsecase, command: str) -> NoReturn:
        raise NotImplementedError()
    
    def set_queue_handler(
        self, queue_name: str,
        handler: Callable, retrying_on_error: bool = False
    ) -> NoReturn:
        raise NotImplementedError()

    def close(self) -> NoReturn:
        raise NotImplementedError()