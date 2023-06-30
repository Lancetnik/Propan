class RabbitBroker(BrokerAsyncUsecase):
    def _get_log_context(
        self,
        message: Optional[PropanMessage],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
    ) -> Dict[str, Any]:
        return {
            "queue": queue.name,
            "exchange": exchange.name if exchange else "default",
            **super()._get_log_context(message),
        }
