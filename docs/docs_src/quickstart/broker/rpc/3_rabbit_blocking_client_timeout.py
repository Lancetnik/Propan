await broker.publish(
    "hi!",
    queue="ping",
    callback=True,
    callback_timeout=3.0  # (1)
)