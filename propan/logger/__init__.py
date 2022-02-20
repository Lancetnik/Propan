from .adapter.loguru_usecase import LoguruAdapter
from .composition import LoggerSimpleComposition
from .utils import ignore_exceptions


logger = LoguruAdapter()

__all__ = (
    'logger',
    'ignore_exceptions',
    'LoggerSimpleComposition'
)
