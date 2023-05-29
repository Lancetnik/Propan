from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@127.0.0.1/")

@broker.handle("ping")
async def ping(m: str):
    return "pong!"  # <-- send RPC response
