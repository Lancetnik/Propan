from itertools import dropwhile
from functools import wraps
import traceback
from typing import Iterable, Callable

from propan.logger.model.usecase import LoggerUsecase
from propan.config.lazy import settings


def ignore_exceptions(logger: LoggerUsecase, ignored: Iterable[Exception]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ignored as e:
                logger.error(e)
        return wrapper
    return decorator


def find_trace() -> str:
    file = catch_call()
    filepath = file.filename.split(f'{settings.BASE_DIR}/')
    if len(filepath) == 1:
        path = filepath[0]
    else:
        path = filepath[1]
    path = path.rstrip('.py').replace('/', '.')
    func_name = file.name
    line = file.lineno
    if 'propan' in path:
        file = path.split(".")[-1]
        return f'{file}:{func_name}:{line}'
    return f'{path}:{func_name}:{line}'


def catch_call(ignore='logger') -> traceback.FrameSummary:
    # получаем пути файлов из стека вызовов
    trace = traceback.StackSummary.extract(traceback.walk_stack(None))
    # отсеиваем все вызовы из директории "logger" и берем первый снаружи
    called_from = list(dropwhile(lambda x: ignore in x.filename, trace))[0]
    return called_from
