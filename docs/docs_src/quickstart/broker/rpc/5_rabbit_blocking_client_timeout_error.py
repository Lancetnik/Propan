await broker.publish(
    "hi!",
    queue="ping",
    callback=True,
    raise_timeout=True
)