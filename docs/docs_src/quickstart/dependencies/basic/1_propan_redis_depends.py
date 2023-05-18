from propan import PropanApp, RedisBroker, Depends

broker = RedisBroker("redis://localhost:6379")
app = PropanApp(broker)

def simple_dependency():
    return 1

@broker.handle("test")
async def handler(body: dict, d: int = Depends(simple_dependency)):
    assert d == 1