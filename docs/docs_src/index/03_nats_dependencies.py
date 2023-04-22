from propan import PropanApp, Context, NatsBroker

gl_broker = NatsBroker("nats://localhost:4222")
app = PropanApp(gl_broker)

@gl_broker.handle("test")
async def base_handler(body: dict,
                       broker: NatsBroker = Context()):
    assert broker is gl_broker
