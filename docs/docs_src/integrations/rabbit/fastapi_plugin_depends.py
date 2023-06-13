from fastapi import FastAPI, Depends
from propan import RabbitBroker
from propan.fastapi import RabbitRouter
from typing_extensions import Annotated

router = RabbitRouter("amqp://guest:guest@localhost:5672")

app = FastAPI(lifespan=router.lifespan_context)

def broker():
    return router.broker

@router.get("/")
async def hello_http(broker: Annotated[RabbitBroker, Depends(broker)]):
    await broker.publish("Hello, Rabbit!", "test")
    return "Hello, HTTP!"

app.include_router(router)