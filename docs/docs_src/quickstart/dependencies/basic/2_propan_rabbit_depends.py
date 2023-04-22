from propan import PropanApp, RabbitBroker, Depends

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)

def another_dependency():
    return 1

def simple_dependency(b: int = Depends(another_dependency)): # (1)
    return b * 2

@broker.handle("test")
async def handler(
    body: dict,
    a: int = Depends(another_dependency),
    b: int = Depends(simple_dependency)):
    assert (a + b) == 3