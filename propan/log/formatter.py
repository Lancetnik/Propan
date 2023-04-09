import logging
import sys
from collections import defaultdict
from typing import Callable, Optional

import click
from propan.utils.context.main import log_context


class ColourizedFormatter(logging.Formatter):
    level_name_colors: "defaultdict[str, Callable[[str], str]]" = defaultdict(
        lambda: str,
        **{
            str(logging.DEBUG): lambda level_name: click.style(
                str(level_name), fg="cyan"
            ),
            str(logging.INFO): lambda level_name: click.style(
                str(level_name), fg="green"
            ),
            str(logging.WARNING): lambda level_name: click.style(
                str(level_name), fg="yellow"
            ),
            str(logging.ERROR): lambda level_name: click.style(
                str(level_name), fg="red"
            ),
            str(logging.CRITICAL): lambda level_name: click.style(
                str(level_name), fg="bright_red"
            ),
        },
    )

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        use_colors: Optional[bool] = None,
    ):
        """
        Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default as described above. Allow for specialized date formatting with
        the optional datefmt argument. If datefmt is omitted, you get an
        ISO8601-like (or RFC 3339-like) format.

        Use a style parameter of '%', '{' or '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting or
        :class:`string.Template` formatting in your format string.
        """
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        return self.level_name_colors[str(level_no)](level_name)

    def formatMessage(self, record: logging.LogRecord) -> str:
        levelname = expand_log_field(record.levelname, 8)
        if self.use_colors is True:  # pragma: no cover
            levelname = self.color_level_name(levelname, record.levelno)
        record.__dict__["levelname"] = levelname
        return super().formatMessage(record)


class DefaultFormatter(ColourizedFormatter):
    pass


class AccessFormatter(ColourizedFormatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        context = log_context.get()
        if context:  # pragma: no cover
            record.__dict__.update(context)
        return super().formatMessage(record)


def expand_log_field(field: str, symbols: int) -> str:
    return field + (" " * (symbols - len(field)))
