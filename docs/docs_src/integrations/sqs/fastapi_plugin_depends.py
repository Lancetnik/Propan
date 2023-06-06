from fastapi import FastAPI, Depends
from propan import SQSBroker
from propan.fastapi import SQSRouter
from typing_extensions import Annotated

router = SQSRouter("http://localhost:9324")

app = FastAPI(lifespan=router.lifespan_context)

def broker():
    return router.broker

@router.get("/")
async def hello_http(broker: Annotated[SQSBroker, Depends(broker)]):
    await broker.publish("Hello, SQS!", "test")
    return "Hello, HTTP!"

app.include_router(router)