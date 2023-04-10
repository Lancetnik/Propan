from fastapi import FastAPI
from propan.brokers.nats import NatsBroker

broker = NatsBroker("nats://localhost:4222")

app = FastAPI()

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.on_event("startup")
async def start_broker():
    await broker.start()

@app.on_event("shutdown")
async def stop_broker():
    await broker.close()