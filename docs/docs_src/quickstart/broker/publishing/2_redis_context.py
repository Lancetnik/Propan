async with RedisBroker("redis://localhost:6379") as broker:
    await broker.publish(m, "another-channel")