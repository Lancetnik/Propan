import sys

from propan.log.formatter import DefaultFormatter


def test_init():
    assert DefaultFormatter().use_colors is sys.stdout.isatty()
    assert DefaultFormatter(use_colors=True).use_colors is True
    assert DefaultFormatter(use_colors=False).use_colors is False
