from fastapi import FastAPI
from propan.fastapi import KafkaRouter

app = FastAPI()

router = KafkaRouter("localhost:9092")

@router.get("/")
async def hello_http():
    await router.broker.publish("Hello, Kafka!", "test")
    return "Hello, HTTP!"

app.include_router(router)