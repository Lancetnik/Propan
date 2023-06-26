from propan import RabbitBroker

async def custom_decode(msg, original_decoded):
    return original_decoded(msg)

broker = RabbitBroker(decode_message=custom_decode)

@broker.handle("test", decode_message=custom_decode)
async def handler(): ...