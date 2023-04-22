from propan import PropanApp, NatsBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = NatsBroker()
    app.set_broker(broker)