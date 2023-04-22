from propan import PropanApp, NatsBroker

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)