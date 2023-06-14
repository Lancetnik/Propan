import asyncio
from typing import Any, Optional


import aio_pika
from propan.brokers._model import BrokerUsecase

class RabbitBroker(BrokerUsecase):
    _connection: Optional[aio_pika.RobustConnection]
    _channel: Optional[aio_pika.RobustChannel]

    async def _connect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> aio_pika.RobustConnection:
        connection = await aio_pika.connect_robust(
            *args, **kwargs, loop=asyncio.get_event_loop()
        )

        if self._channel is None:
            self._channel = await connection.channel()

        return connection
