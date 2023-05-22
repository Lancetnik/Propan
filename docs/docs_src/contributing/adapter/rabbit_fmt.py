class RabbitBroker(BrokerUsecase):
    __max_exchange_len: int
    __max_queue_len: int

    def __init__(
        self,
        *args: Any,
        log_fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, log_fmt=log_fmt, **kwargs)

        self.__max_queue_len = 4
        self.__max_exchange_len = 4

    @property
    def fmt(self) -> str:
        return super().fmt or (
            "%(asctime)s %(levelname)s - "
            f"%(exchange)-{self.__max_exchange_len}s | "
            f"%(queue)-{self.__max_queue_len}s | "
            f"%(message_id)-10s "
            "- %(message)s"
        )
