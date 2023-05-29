from fastapi import FastAPI
from propan.fastapi import SQSRouter

app = FastAPI()

router = SQSRouter("http://localhost:9324")

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, SQS!", "test")
    return "Hello, HTTP!"

app.include_router(router)