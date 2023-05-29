from fastapi import FastAPI
from propan.fastapi import RedisRouter

app = FastAPI()

router = RedisRouter("redis://localhost:6379")

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, Redis!", "test")
    return "Hello, HTTP!"

app.include_router(router)