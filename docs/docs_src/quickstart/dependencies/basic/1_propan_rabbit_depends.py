from propan import PropanApp, RabbitBroker, Depends

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)

def simple_dependency():
    return 1

@broker.handle("test")
async def handler(body: dict, d: int = Depends(simple_dependency)):
    assert d == 1