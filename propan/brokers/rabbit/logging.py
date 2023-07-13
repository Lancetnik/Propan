from typing import Any, Optional

from propan.brokers._model.schemas import PropanMessage
from propan.brokers.rabbit.schemas import RabbitExchange, RabbitQueue
from propan.types import AnyDict


class RabbitLoggingMixin:
    _max_queue_len: int
    _max_exchange_len: int

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
