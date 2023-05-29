from propan import PropanApp, NatsBroker, Depends

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)

def simple_dependency():
    return 1

@broker.handle("test")
async def handler(body: dict, d: int = Depends(simple_dependency)):
    assert d == 1