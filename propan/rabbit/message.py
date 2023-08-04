import aio_pika

from propan.broker.message import PropanMessage
from propan.types import AnyDict


class RabbitMessage(PropanMessage[aio_pika.IncomingMessage]):
    async def ack(self, **kwargs: AnyDict) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.ack()

    async def nack(self, **kwargs: AnyDict) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.nack()

    async def reject(self, **kwargs: AnyDict) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.reject()
