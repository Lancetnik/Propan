from logging import Logger
from propan import Context, Depends

...

async def base_dep(body: dict) -> bool:
    return True

@broker.handle("test")
async def base_handler(body: dict,
                       dep: bool = Depends(base_dep),
                       logger: Logger = Context()):
    assert dep is True
    logger.info(body)
