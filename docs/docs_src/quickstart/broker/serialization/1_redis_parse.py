from propan import PropanMessage

async def parse_message(
    message: bytes
) -> PropanMessage[bytes]:
    return PropanMessage(
        body=message,
        raw_message=message,
    )