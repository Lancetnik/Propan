from fastapi import FastAPI
from propan.fastapi import NatsRouter

router = NatsRouter("nats://localhost:4222")

app = FastAPI(lifespan=router.lifespan_context)

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, Nats!", "test")
    return "Hello, HTTP!"

app.include_router(router)