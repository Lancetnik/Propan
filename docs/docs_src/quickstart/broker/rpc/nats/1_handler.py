from propan import NatsBroker

broker = NatsBroker("nats://localhost:4222")

@broker.handle("ping")
async def ping(m: str):
    return "pong!"  # <-- send RPC response
