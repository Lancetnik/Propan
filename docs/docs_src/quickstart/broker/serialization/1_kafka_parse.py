from aiokafka.structs import ConsumerRecord
from propan import PropanMessage

async def parse_message(
    message: ConsumerRecord
) -> PropanMessage[ConsumerRecord]:
    headers = {i: j.decode() for i, j in message.headers}
    return PropanMessage(
        body=message.value,
        raw_message=message,
        message_id=f"{message.offset}-{message.timestamp}",
        reply_to=headers.get("reply_to", ""),
        content_type=headers.get("content-type"),
        headers=headers,
    )
