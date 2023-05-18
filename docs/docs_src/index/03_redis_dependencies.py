from propan import PropanApp, RedisBroker, Context, Depends

broker = RedisBroker("redis://localhost:6379")
app = PropanApp(gl_broker)

async def base_dep(body: dict) -> bool:
    return True

@gl_broker.handle("test")
async def base_handler(body: dict,
                       dep: bool = Depends(base_dep),
                       broker: RedisBroker = Context()):
    assert dep is True
    assert broker is gl_broker
