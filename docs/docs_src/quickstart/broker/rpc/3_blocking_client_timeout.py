await broker.publish(
    "hi!", "ping",
    callback=True,
    callback_timeout=3.0  # (1)
)