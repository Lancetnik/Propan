import logging
from enum import Enum
from collections import defaultdict
from typing import Union

from propan.log import access_logger, logger


class LogLevels(str, Enum):
    critical = "critical"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


LOG_LEVELS: "defaultdict[str, int]" = defaultdict(lambda: logging.INFO, **{
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
})


def set_log_level(level: Union[LogLevels, str]) -> None:
    if isinstance(level, LogLevels):
        level = level.value
    log_level = LOG_LEVELS[level]
    logger.setLevel(log_level)
    access_logger.setLevel(log_level)
