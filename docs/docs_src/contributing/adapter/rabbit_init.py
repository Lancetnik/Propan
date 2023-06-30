from typing import Any, Optional

from propan.brokers._model import BrokerAsyncUsecase


class RabbitBroker(BrokerAsyncUsecase):
    def __init__(
        self,
        *args: Any,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, log_fmt=log_fmt, **kwargs)
