await broker.publish(
    "hi!",
    channel="ping",
    callback=True,
    callback_timeout=None
)