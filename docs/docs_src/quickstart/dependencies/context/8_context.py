from propan.annotations import ContextRepo

@broker.hanlde("test")
async def handler(
    body: dict,
    context: ContextRepo
):
    context.set_global("my_key", 1)