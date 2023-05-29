from fastapi import FastAPI, Depends
from propan import RedisBroker
from propan.fastapi import RedisRouter
from typing_extensions import Annotated

app = FastAPI()

router = RedisRouter("redis://localhost:6379")

def broker():
    return router.broker

@router.get("/")
async def hello_http(broker: Annotated[RedisBroker, Depends(broker)]):
    await broker.publish("Hello, Redis!", "test")
    return "Hello, HTTP!"

app.include_router(router)