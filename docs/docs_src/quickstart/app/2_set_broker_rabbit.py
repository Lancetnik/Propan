from propan import PropanApp, RabbitBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
    app.set_broker(broker)