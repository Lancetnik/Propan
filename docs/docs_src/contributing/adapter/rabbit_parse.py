import aio_pika

from propan.brokers.model import BrokerUsecase
from propan.brokers.model.schemas import PropanMessage


class RabbitBroker(BrokerUsecase):
    ...
    @staticmethod
    async def _parse_message(
        message: aio_pika.message.IncomingMessage,
    ) -> PropanMessage:
        return PropanMessage(
            body=message.body,
            headers=message.headers,
            reply_to=message.reply_to or "",
            message_id=message.message_id,
            content_type=message.content_type or "",
            raw_message=message,
        )
