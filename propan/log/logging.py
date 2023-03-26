import logging
import logging.config
from typing import Dict, Any
from functools import partial

from propan.log.formatter import DefaultFormatter, AccessFormatter


def configure_formatter(formatter, *args, **kwargs):
    return formatter(*args, **kwargs)


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": partial(configure_formatter, DefaultFormatter),
            "fmt": "%(asctime)s %(levelname)s - %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": partial(configure_formatter, AccessFormatter),
            "fmt": '%(asctime)s %(levelname)s - %(message)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "propan": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "propan.error": {"level": "INFO"},
        "propan.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


logger = logging.getLogger("propan")
access_logger = logging.getLogger("propan.access")
