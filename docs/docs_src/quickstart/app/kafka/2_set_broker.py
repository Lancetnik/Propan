from propan import PropanApp, KafkaBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = KafkaBroker("localhost:9092")
    app.set_broker(broker)