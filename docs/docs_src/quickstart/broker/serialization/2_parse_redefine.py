from propan import RabbitBroker

async def custom_parse(msg, original_parser):
    return original_parser(msg)

broker = RabbitBroker(parse_message=custom_parse)

@broker.handle("test", parse_message=custom_parse)
async def handler(): ...