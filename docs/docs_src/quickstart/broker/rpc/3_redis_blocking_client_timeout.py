await broker.publish(
    "hi!",
    channel="ping",
    callback=True,
    callback_timeout=3.0  # (1)
)