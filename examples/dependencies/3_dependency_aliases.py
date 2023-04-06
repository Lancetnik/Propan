'''
Using Alias allows you rename context dependencies passing
to your function
'''
from propan.app import PropanApp
from propan.utils import Alias
from propan.brokers.rabbit import RabbitBroker


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@app.on_startup
def setup(rabbit: RabbitBroker = Alias("broker")):
    assert rabbit is broker
