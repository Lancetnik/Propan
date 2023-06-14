from typing import Any, Optional

from propan.brokers._model import BrokerUsecase


class RabbitBroker(BrokerUsecase):
    def __init__(
        self,
        *args: Any,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, log_fmt=log_fmt, **kwargs)
