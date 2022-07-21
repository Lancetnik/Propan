from typing import Protocol, Callable, Dict

from propan.logger.model.usecase import LoggerUsecase

from .bus_connection import ConnectionData


class BrokerUsecase(Protocol):
    handlers: Dict[str, Callable] = {}

    def connect(self, connection_data: ConnectionData):
        raise NotImplementedError()

    def init_channel(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        raise NotImplementedError()

    def publish_message(self, queue_name: str, message: str) -> None:
        raise NotImplementedError()

    def process_message(logger: LoggerUsecase, command: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()
