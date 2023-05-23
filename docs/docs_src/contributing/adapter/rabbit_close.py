class RabbitBroker(BrokerUsecase):
    ...

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None

        if self._connection is not None:
            await self._connection.close()
            self._connection = None
