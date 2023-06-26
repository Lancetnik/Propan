from aio_pika.message import IncomingMessage
from propan import PropanMessage

async def parse_message(
    message: IncomingMessage
) -> PropanMessage[IncomingMessage]:
    return PropanMessage(
        body=message.body,
        headers=message.headers,
        reply_to=message.reply_to or "",
        message_id=message.message_id,
        content_type=message.content_type or "",
        raw_message=message,
    )
