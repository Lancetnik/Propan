from typing import Protocol, Callable, Dict, Union

from propan.logger.model.usecase import LoggerUsecase

from .bus_connection import ConnectionData
from .schemas import Queue


class BrokerUsecase(Protocol):
    handlers: Dict[str, Callable] = {}

    def connect(self, connection_data: ConnectionData):
        raise NotImplementedError()

    def init_channel(self) -> None:
        raise NotImplementedError()

    def start(self) -> None:
        raise NotImplementedError()

    def set_handler(self, queue_name: Union[str, Queue], func: Callable, **broker_args) -> None:
        raise NotImplementedError()

    def publish_message(self, queue_name: str, message: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()
