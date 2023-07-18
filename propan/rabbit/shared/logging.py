import logging
from typing import Any, Optional

from propan.broker.core.mixins import LoggingMixin
from propan.broker.message import PropanMessage
from propan.log import access_logger
from propan.rabbit.shared.schemas import RabbitExchange, RabbitQueue
from propan.types import AnyDict


class RabbitLoggingMixin(LoggingMixin):
    _max_queue_len: int
    _max_exchange_len: int

    def __init__(
        self,
        *args: Any,
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: str | None = None,
        **kwargs: AnyDict,
    ) -> None:
        super().__init__(
            logger=logger,
            log_level=log_level,
            log_fmt=log_fmt,
        )
        self._max_queue_len = 4
        self._max_exchange_len = 4

    def _get_log_context(
        self,
        message: Optional[PropanMessage[Any]],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
    ) -> AnyDict:
        context = {
            "queue": queue.name,
            "exchange": exchange.name if exchange else "default",
            **super()._get_log_context(message),
        }
        return context

    @property
    def fmt(self) -> str:
        return super().fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(exchange)-{self._max_exchange_len}s | "
            f"%(queue)-{self._max_queue_len}s | "
            f"%(message_id)-10s "
            "- %(message)s"
        )

    def _setup_log_context(
        self,
        queue: Optional[RabbitQueue] = None,
        exchange: Optional[RabbitExchange] = None,
    ) -> None:
        if exchange is not None:
            self._max_exchange_len = max(self._max_exchange_len, len(exchange.name))

        if queue is not None:  # pragma: no branch
            self._max_queue_len = max(self._max_queue_len, len(queue.name))
