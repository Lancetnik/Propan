from propan import PropanApp, RabbitBroker, Context, Depends

gl_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(gl_broker)

async def base_dep(body: dict) -> bool:
    return True

@gl_broker.handle("test")
async def base_handler(body: dict,
                       dep: bool = Depends(base_dep),
                       broker: RabbitBroker = Context()):
    assert dep is True
    assert broker is gl_broker