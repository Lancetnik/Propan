import aio_pika

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.schemas import PropanMessage


class RabbitBroker(BrokerAsyncUsecase):
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
