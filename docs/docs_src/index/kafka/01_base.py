from propan import PropanApp, KafkaBroker

broker = KafkaBroker("localhost:9092")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    print(body)