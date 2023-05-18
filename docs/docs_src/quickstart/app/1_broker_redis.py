from propan import PropanApp, RedisBroker

broker = RedisBroker("redis://localhost:6379")
app = PropanApp(broker)