from propan import PropanApp, NatsBroker, Context, Depends

gl_broker = NatsBroker("nats://localhost:4222")
app = PropanApp(gl_broker)

async def base_dep(body: dict) -> bool:
    return True

@gl_broker.handle("test")
async def base_handler(body: dict,
                       dep: bool = Depends(base_dep),
                       broker: NatsBroker = Context()):
    assert dep is True
    assert broker is gl_broker
