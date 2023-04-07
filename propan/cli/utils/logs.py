import logging
from enum import Enum
from typing import Dict

from propan.log import access_logger, logger


class LogLevels(str, Enum):
    critical = "critical"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


LOG_LEVELS: Dict[str, int] = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def set_log_level(level: LogLevels) -> None:
    log_level = LOG_LEVELS[level.value]
    logger.setLevel(log_level)
    access_logger.setLevel(log_level)
