from propan import annotations

@rabbit_broker.handle("test")
async def base_handler(
    body: dict,
    app: annotations.App,
    context: annotations.ContextRepo,
    logger: annotations.Logger,
    broker: annotations.RabbitBroker,
    message: annotations.RabbitMessage,
):
    ...
