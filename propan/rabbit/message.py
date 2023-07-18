import aio_pika

from propan.broker.message import PropanMessage


class RabbitMessage(PropanMessage[aio_pika.IncomingMessage]):
    async def ack(self) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.ack()

    async def nack(self) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.nack()

    async def reject(self) -> None:
        pika_message = self.raw_message
        if (
            pika_message._IncomingMessage__processed
            or pika_message._IncomingMessage__no_ack
        ):
            return
        await pika_message.reject()
