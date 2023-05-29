from fastapi import FastAPI, Depends
from propan import NatsBroker
from propan.fastapi import NatsRouter
from typing_extensions import Annotated

app = FastAPI()

router = NatsRouter("nats://localhost:4222")

def broker():
    return router.broker

@router.get("/")
async def hello_http(broker: Annotated[NatsBroker, Depends(broker)]):
    await broker.publish("Hello, Nats!", "test")
    return "Hello, HTTP!"

app.include_router(router)