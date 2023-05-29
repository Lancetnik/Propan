from propan import PropanApp, SQSBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = SQSBroker("http://localhost:9324", ...)
    app.set_broker(broker)