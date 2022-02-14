from functools import wraps
import sys

from loguru import logger

from ..model.usecase import LoggerUsecase
from ..utils import find_trace


logger.remove()
logger.add(sys.stderr, format="<green>{time:DD.MM.YYYY HH:mm:ss.SSS}</green> | <cyan>{name}</cyan> | <level>{message}</level>")

def patching(record):
    record['name'] = find_trace()

logger = logger.patch(patching)


class LoguruAdapter(LoggerUsecase):
    def info(self, message: str):
        logger.info(message)

    def debug(self, message: str):
        logger.debug(message)

    def error(self, message: str):
        logger.error(message)

    def success(self, message: str):
        logger.success(message)

    def warning(self, message: str):
        logger.warning(message)

    def catch(self, func, reraise: bool = False):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            return await logger.catch(
                func,
                reraise=reraise
            )(*args, **kwargs)
        return wrapped
