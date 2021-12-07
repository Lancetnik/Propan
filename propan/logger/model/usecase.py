from typing import Protocol, NoReturn, Callable


class LoggerUsecase(Protocol):
    not_catch: tuple[Exception]

    def info(self, message: str) -> NoReturn:
        raise NotImplementedError()

    def error(self, message: str) -> NoReturn:
        raise NotImplementedError()

    def debug(self, message: str) -> NoReturn:
        raise NotImplementedError()

    def success(self, message: str) -> NoReturn:
        raise NotImplementedError()

    def warning(self, message: str) -> NoReturn:
        raise NotImplementedError()

    def catch(self, func: Callable) -> Callable:
        raise NotImplementedError()

    def _catch_base(self, func: Callable) -> Callable:
        raise NotImplementedError()