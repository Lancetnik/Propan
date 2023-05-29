await broker.publish(
    "hi!", "ping",
    callback=True,
    raise_timeout=True
)