import logging

import pytest

from propan.cli.utils.logs import LOG_LEVELS, LogLevels, set_log_level
from propan.log import access_logger, logger


@pytest.mark.parametrize(
    "level",
    (
        *LogLevels._member_map_.values(),
        *LogLevels.__members__.values(),
    ),
)
def test_set_level(level):
    set_log_level(level)
    if isinstance(level, LogLevels):
        level = level.value
    assert access_logger.level is logger.level is LOG_LEVELS[level]


def test_set_default():
    level = "wrong_level"
    set_log_level(level)
    assert access_logger.level is logger.level is LOG_LEVELS[level] is logging.INFO
