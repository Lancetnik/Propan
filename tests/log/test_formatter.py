import logging
import sys

from propan.log.formatter import AccessFormatter, DefaultFormatter
from propan.utils.context import log_context


def test_init():
    assert DefaultFormatter().use_colors is sys.stdout.isatty()
    assert DefaultFormatter(use_colors=True).use_colors is True
    assert DefaultFormatter(use_colors=False).use_colors is False


def test_use_colors():
    formatter = DefaultFormatter(
        fmt="%(asctime)s %(levelname)s - %(message)s", use_colors=True
    )
    record = logging.LogRecord("test", logging.INFO, "test", 1, "hello", None, None)
    assert "\033" in formatter.format(record)


def test_context():
    class PatchedFormatter(AccessFormatter):
        def formatMessage(self, record: logging.LogRecord) -> str:
            super().formatMessage(record)
            assert getattr(record, "key", None) == 1

    log_context.set({"key": 1})

    formatter = PatchedFormatter(use_colors=True)

    record = logging.LogRecord("test", logging.INFO, "test", 1, "hello", None, None)
    formatter.format(record)
