from propan import PropanApp, NatsBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = NatsBroker("nats://localhost:4222")
    app.set_broker(broker)