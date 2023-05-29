from propan import PropanApp, KafkaBroker

broker = KafkaBroker("localhost:9092")
app = PropanApp(broker)