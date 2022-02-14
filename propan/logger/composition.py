from collections import namedtuple
from functools import wraps

from .model.usecase import LoggerUsecase


PriorityPair = namedtuple("PriorityPair", ["logger", "priority"])

class LoggerSimpleComposition(LoggerUsecase):
    loggers: list[LoggerUsecase]
    not_catch: tuple[Exception]

    def __init__(
        self,
        loggers: tuple[PriorityPair[LoggerUsecase, int]],
        not_catch: tuple[Exception] = tuple()
    ):
        self.loggers = tuple(
            logger for logger, priority in
            sorted(loggers, key=lambda x: x.priority)
        )
        self.not_catch = not_catch
        for logger in self.loggers:
            logger.not_catch = not_catch

    def info(self, message: str):
        for logger in self.loggers:
            logger.info(message)

    def debug(self, message: str):
        for logger in self.loggers:
            logger.debug(message)

    def error(self, message: str):
        for logger in self.loggers:
            logger.error(message)

    def warning(self, message: str):
        for logger in self.loggers:
            logger.warning(message)

    def success(self, message: str):
        for logger in self.loggers:
            logger.success(message)

    def catch(self, func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            new_func = func
            for logger in self.loggers[:-1]:
                new_func = logger.catch(new_func, reraise=True)
            new_func = self.loggers[-1].catch(new_func)

            return await new_func(*args, **kwargs)
        return wrapped
