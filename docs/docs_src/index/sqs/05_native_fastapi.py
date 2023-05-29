from fastapi import Depends, FastAPI
from pydantic import BaseModel
from propan.fastapi import SQSRouter

app = FastAPI()

router = SQSRouter("http://localhost:9324")

class Incoming(BaseModel):
    m: dict

def call():
    return True

@router.event("test")
async def hello(m: Incoming, d = Depends(call)) -> dict:
    return { "response": "Hello, world!"}

app.include_router(router)