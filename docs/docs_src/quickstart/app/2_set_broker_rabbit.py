from propan import PropanApp, RabbitBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = RabbitBroker()
    app.set_broker(broker)