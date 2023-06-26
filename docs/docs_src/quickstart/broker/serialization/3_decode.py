import json
from propan import PropanMessage

async def decode_message(message: PropanMessage):
    body = message.body
    if message.content_type is not None:
        return json.loads(body.decode())
    else:
        return body