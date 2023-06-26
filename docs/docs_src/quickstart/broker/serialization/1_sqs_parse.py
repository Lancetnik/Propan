from typing import Dict, Any
from propan import PropanMessage

async def parse_message(
    message: Dict[str, Any],
) -> PropanMessage[Dict[str, Any]]:
    attributes = message.get("MessageAttributes", {})
    headers = {i: j.get("StringValue") for i, j in attributes.items()}
    return PropanMessage(
        body=message.get("Body", "").encode(),
        message_id=message.get("MessageId"),
        content_type=headers.pop("content-type", None),
        reply_to=headers.pop("reply_to", None) or "",
        headers=headers,
        raw_message=message,
    )