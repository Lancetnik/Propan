from fastapi import FastAPI
from propan.fastapi import SQSRouter

router = SQSRouter("http://localhost:9324")

app = FastAPI(lifespan=router.lifespan_context)

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, SQS!", "test")
    return "Hello, HTTP!"

app.include_router(router)