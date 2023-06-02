from propan import NatsBroker

async def main():
    async with NatsBroker("nats://localhost:4222") as broker:
        r = await broker.publish(
            "hi!", "ping",
            callback=True
        )

    assert r == "pong"  # <-- take the RPC response