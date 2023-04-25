async with NatsBroker("nats://localhost:4222") as broker:
    await broker.publish(m, "another-queue")