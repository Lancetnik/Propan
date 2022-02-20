from typing import Protocol, Callable, Tuple


class LoggerUsecase(Protocol):
    not_catch: Tuple[Exception]

    def info(self, message: str) -> None:
        raise NotImplementedError()

    def error(self, message: str) -> None:
        raise NotImplementedError()

    def debug(self, message: str) -> None:
        raise NotImplementedError()

    def success(self, message: str) -> None:
        raise NotImplementedError()

    def warning(self, message: str) -> None:
        raise NotImplementedError()

    def catch(self, func: Callable) -> Callable:
        raise NotImplementedError()

    def _catch_base(self, func: Callable) -> Callable:
        raise NotImplementedError()