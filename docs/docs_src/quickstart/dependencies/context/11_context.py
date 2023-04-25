from propan import Context, Depends

def nested_func(
    body: dict,
    logger = Context()
):
    logger.info(body)
    return body

@broker.hanlde("test")
async def handler(body: dict, n = Depends(nested_func)):
    pass