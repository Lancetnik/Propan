from propan import PropanApp, SQSBroker, Depends

broker = SQSBroker("http://localhost:9324", ...)
app = PropanApp(broker)

def simple_dependency():
    return 1

@broker.handle("test")
async def handler(body: dict, d: int = Depends(simple_dependency)):
    assert d == 1