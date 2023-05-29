from propan import PropanApp, RedisBroker

broker = RedisBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
    if msg == "ping":
        return "pong"
    else:
        return "wrong"

app = PropanApp(broker)