from propan import RedisBroker

broker = RedisBroker("redis://localhost:6379")

@broker.handle("ping")
async def ping(m: str):
    return "pong!"  # <-- send RPC response
