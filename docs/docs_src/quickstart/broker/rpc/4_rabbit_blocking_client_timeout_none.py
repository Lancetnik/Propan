await broker.publish(
    "hi!",
    queue="ping",
    callback=True,
    callback_timeout=None
)