from propan import PropanApp, RedisBroker

app = PropanApp()

@app.on_startup
def init_broker():
    broker = RedisBroker("redis://localhost:6379")
    app.set_broker(broker)