from fastapi import FastAPI
from propan.fastapi import RedisRouter

router = RedisRouter("redis://localhost:6379")

app = FastAPI(lifespan=router.lifespan_context)

@router.after_startup
def do_smth(app: FastAPI):
    ...

@router.after_startup
async def publish_smth(app: FastAPI):
    await router.broker.publish(...)

app.include_router(router)