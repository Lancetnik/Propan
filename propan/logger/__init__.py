from propan.logger.adapter.loguru_usecase import LoguruAdapter
from propan.logger.adapter.empty import empty
from propan.logger.composition import LoggerSimpleComposition
from propan.logger.utils import ignore_exceptions


loguru = LoguruAdapter()

__all__ = (
    'loguru',
    'empty'
    'ignore_exceptions',
    'LoggerSimpleComposition'
)
