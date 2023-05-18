await broker.publish(
    "hi!",
    channel="ping",
    callback=True,
    raise_timeout=True
)