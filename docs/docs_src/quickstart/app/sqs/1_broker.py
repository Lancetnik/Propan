from propan import PropanApp, SQSBroker

broker = SQSBroker("http://localhost:9324", ...)
app = PropanApp(broker)