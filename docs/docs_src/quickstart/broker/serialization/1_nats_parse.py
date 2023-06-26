from nats.aio.msg import Msg
from propan import PropanMessage

async def parse_message(
    message: Msg
) -> PropanMessage[Msg]:
    return PropanMessage(
        body=message.data,
        content_type=message.header.get("content-type", ""),
        headers=message.header,
        reply_to=message.reply,
        raw_message=message,
    )
