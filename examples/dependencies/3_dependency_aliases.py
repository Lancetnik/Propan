"""
Using Alias allows you rename context dependencies passing
to your function
"""
from propan import Context, PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@app.on_startup
def setup(rabbit: RabbitBroker = Context("broker")):
    assert rabbit is broker
