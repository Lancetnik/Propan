async with SQSBroker("http://localhost:9324", ...) as broker:
    await broker.publish(m, "another-queue")