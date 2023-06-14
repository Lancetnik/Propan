from propan import PropanApp, RabbitBroker
from propan.brokers.rabbit import RabbitQueue, RabbitExchange, ExchangeType

broker = RabbitBroker()
app = PropanApp(
    broker=broker,
    title="Smartylighting Streetlights Propan API",
    version="1.0.0",
    description="""
    The Smartylighting Streetlights API.
    ### Check out its awesome features:
    * Turn a specific streetlight on/off 🌃
    * Receive real-time information about environmental 📈
    """
)

@broker.handle(
    queue=RabbitQueue("*.info", durable=True),
    exchange=RabbitExchange("logs", durable=True, type=ExchangeType.TOPIC)
)
async def handle_logs(level: int, message: str = ""):
    """Handle all environmental events"""
    ...
