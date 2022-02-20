from .adapter.loguru_usecase import LoguruAdapter
from .composition import LoggerSimpleComposition
from .utils import ignore_exceptions


loguru = LoguruAdapter()

__all__ = (
    'loguru',
    'ignore_exceptions',
    'LoggerSimpleComposition'
)
