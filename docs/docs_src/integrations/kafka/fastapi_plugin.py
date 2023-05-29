from fastapi import Depends, FastAPI
from pydantic import BaseModel
from propan.fastapi import KafkaRouter

app = FastAPI()

router = KafkaRouter("localhost:9092")

class Incoming(BaseModel):
    m: dict

def call():
    return True

@router.event("test")
async def hello(m: Incoming, d = Depends(call)) -> dict:
    return { "response": "Hello, Kafka!" }

@router.get("/")
async def hello_http():
    return "Hello, HTTP!"

app.include_router(router)