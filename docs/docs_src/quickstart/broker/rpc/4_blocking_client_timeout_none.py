await broker.publish(
    "hi!", "ping",
    callback=True,
    callback_timeout=None
)