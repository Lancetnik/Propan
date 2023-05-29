async with KafkaBroker("localhost:9092") as broker:
    await broker.publish(m, "another-topic")