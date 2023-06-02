from propan import PropanApp, SQSBroker

broker = SQSBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
    if msg == "ping":
        return "pong"
    else:
        return "wrong"

app = PropanApp(broker)