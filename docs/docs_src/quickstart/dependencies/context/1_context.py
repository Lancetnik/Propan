from propan import Context

@broker.hanlde("test")
async def handler(broker = Context()):
    await broker.publish("response", "response-queue")