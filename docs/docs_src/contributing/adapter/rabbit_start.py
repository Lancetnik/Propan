class RabbitBroker(BrokerAsyncUsecase):
    ...
    async def start(self) -> None:
        await super().start()

        for handler in self.handlers:
            queue = await self._channel.declare_queue(**handler.queue.dict())
            func = handler.callback
            await queue.consume(func)
