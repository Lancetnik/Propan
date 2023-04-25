from propan import Context

@broker.hanlde("test")
async def handler(
    body: dict,
    some_field: int = Context(default="1", cast=True)
):
    assert some_field == 1