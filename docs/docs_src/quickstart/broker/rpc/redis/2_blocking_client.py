from propan import RedisBroker

async def main():
    async with RedisBroker("redis://localhost:6379") as broker:
        r = await broker.publish(
            "hi!", "ping",
            callback=True
        )

    assert r == "pong"  # <-- take the RPC response