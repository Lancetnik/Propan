from propan import Context

@broker.hanlde("test")
async def handler(
    body: dict,
    some_field = Context(default=None)
):
    assert some_field is None