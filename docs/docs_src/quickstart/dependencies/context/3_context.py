from propan import Context

@broker.hanlde("test")
async def handler(
    body: dict,
    propan_app = Context("app"),
    publish = Context("broker.publish"),
    secret_key = Context("settings.app.secret_key"),
):
    await publish(secret_key, "secret-queue")