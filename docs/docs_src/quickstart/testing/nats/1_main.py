from propan import PropanApp, NatsBroker

broker = NatsBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
    if msg == "ping":
        return "pong"
    else:
        return "wrong"

app = PropanApp(broker)