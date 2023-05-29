async with RabbitBroker("amqp://guest:guest@localhost:5672/") as broker:
    await broker.publish(m, "another-queue")