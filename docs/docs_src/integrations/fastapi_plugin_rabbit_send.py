from fastapi import FastAPI
from propan.fastapi import RabbitRouter

app = FastAPI()

router = RabbitRouter("amqp://guest:guest@localhost:5672")

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, Rabbit!", routing_key="test")
    return "Hello, http!"

app.include_router(router)